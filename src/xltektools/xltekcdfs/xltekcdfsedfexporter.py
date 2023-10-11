"""xltekcdfsedfexporter.py
A HDF5 file which contains data for XLTEK EEG data.
"""
# Package Header #
from xltektools.header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from collections.abc import Iterable
from copy import deepcopy
import gc
import datetime
from pathlib import Path
from typing import Any

# Third-Party Packages #
from baseobjects import BaseObject
import numpy as np
from pyedflib import EdfWriter, FILETYPE_EDFPLUS, FILETYPE_BDFPLUS
from pyedflib.highlevel import make_signal_headers, make_header, write_edf

# Local Packages #
from ..xltekcdfs import XLTEKCDFS


# Definitions #
# Classes #
class XLTEKCDFSEDFExporter(BaseObject):

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        cdfs: None = None,
        new_name: str | None = None,
        channel_names: Iterable[str, ...] | None = None,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # New Attributes #
        self.cdfs: XLTEKCDFS | None = None
        self.new_name: str | None = None

        self.channel_names: list = []
        self.fill_value: float = -1000000.0

        # Parent Attributes #
        super().__init__(init=False, **kwargs)

        # Object Construction #
        if init:
            self.construct(
                cdfs=cdfs,
                new_name=new_name,
                channel_names=channel_names,
                **kwargs,
            )

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        cdfs: None = None,
        new_name: str | None = None,
        channel_names: Iterable[str, ...] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:

        """
        if cdfs is not None:
            self.cdfs = cdfs

        if new_name is not None:
            self.new_name = new_name

        if channel_names is not None:
            self.channel_names.clear()
            self.channel_names.extend(channel_names)

        super().construct(**kwargs)

    def write_edf(
        self,
        path: Path,
        signals,
        signal_headers,
        header: dict | None = None,
        digital: bool = False,
        file_type: str | None = None,
    ):
        """
        """
        assert len(signal_headers) == len(signals), 'signals and signal_headers must be same length'

        header = make_header() | ({} if header is None else header)
        annotations = header.get('annotations', [])
        signal_headers = deepcopy(signal_headers)

        if file_type is None:
            ext = path.suffix.lower()
            if ext == ".edf":
                file_type = FILETYPE_EDFPLUS
            elif ext == ".bdf":
                file_type = FILETYPE_BDFPLUS
            else:
                raise ValueError(f"Unknown extension {ext}")
        else:
            if ".edf" in file_type.lower():
                file_type = FILETYPE_EDFPLUS
            elif ".bdf" in file_type.lower():
                file_type = FILETYPE_BDFPLUS
            else:
                raise ValueError(f"Unknown file type {file_type}")

        with EdfWriter(path, n_channels=len(signals), file_type=file_type) as f:
            f.setSignalHeaders(signal_headers)
            f.setHeader(header)
            f.writeSamples(signals, digital=digital)
            for annotation in annotations:
                f.writeAnnotation(*annotation)
        del f

    def formated_save_edf(
        self,
        path: Path,
        signals: list | np.ndarray,
        signal_headers: list[dict[str, Any]],
        header: dict[str, Any],
        digital: bool = False,
        file_type: int = -1,
    ) -> None:
        write_edf(
            edf_file=path.as_posix(),
            signals=signals,
            signal_headers=signal_headers,
            header=header,
            digital=digital,
            file_type=file_type,
        )

    def save_edf(
        self,
        path: Path,
        signals: list | np.ndarray,
        signal_names: list[str],
        signal_kwargs: dict[str, Any],
        header_kwargs: dict[str, Any],
        digital: bool = False,
        file_type: int = -1,
    ) -> None:
        self.formated_save_edf(
            path=path,
            signals=signals,
            signal_headers=make_signal_headers(signal_names, **signal_kwargs),
            header=make_header(**header_kwargs),
            digital=digital,
            file_type=file_type,
        )

    def create_header(self) -> dict:
        info = self.cdfs.meta_information
        return make_header(
            patientcode=self.new_name,
            sex="unknown" if info["sex"] == "U" else info["sex"],
            startdate=info["start"],
            equipment="Natus: XLTEK",
        )

    def export_as_hours(self, path, name: str | None, fill: bool = True):
        name = self.new_name if name is None else name
        edf_header = self.create_header()
        flat_data = self.cdfs.data.as_flattened()
        if fill:
            flat_data.time_tolerance = flat_data.sample_period
            flat_data.insert_missing(fill_method="full", fill_kwargs={"fill_value": -1000000.0})
        change_indices = flat_data.where_shapes_change()
        proxy_ranges = zip((0, *change_indices), (*change_indices, len(flat_data.proxies)))
        hours = set()
        copy_number = 0
        for s, e in proxy_ranges:
            proxies = flat_data.proxies[s:e]
            if proxies:
                p = flat_data.create_proxy()
                p.proxies.extend(proxies)
                if p.shape[1] == len(self.channel_names):
                    n_hours = int((p.end_datetime - p.start_datetime).total_seconds() // 3600) + 1
                    first_hour = p.start_datetime.replace(minute=0, second=0, microsecond=0, nanosecond=0)
                    signal_headers = make_signal_headers(
                        self.channel_names,
                        sample_frequency=p.sample_rate,
                        physical_min=-1000000.0,
                        physical_max=320000.0,
                    )
                    for h in range(n_hours):
                        hour = first_hour + datetime.timedelta(hours=h)
                        if hour in hours:
                            copy_number += 1
                        else:
                            hours.add(first_hour + datetime.timedelta(days=h))
                            copy_number = 0
                        day_data = p.find_data_range(
                            start=first_hour + datetime.timedelta(days=h),
                            stop=first_hour + datetime.timedelta(days=h+1),
                            approx=True,
                            tails=True,
                        )

                        path = path / f"{name}_task-hour{len(hours)}{'' if copy_number == 0 else f'_{copy_number}'}.edf"
                        edf_header["startdate"] = day_data.data.start_datetime
                        self.formated_save_edf(
                            path=path,
                            signals=day_data.data.data.T,
                            signal_headers=signal_headers,
                            header=edf_header,
                        )

    def export_as_days(self, path, name: str | None = None, fill: bool = True):
        name = self.new_name if name is None else name
        edf_header = self.create_header()
        flat_data = self.cdfs.data.as_flattened()
        if fill:
            flat_data.time_tolerance = flat_data.sample_period
            flat_data.insert_missing(fill_method="full", fill_kwargs={"fill_value": self.fill_value})
        change_indices = flat_data.where_shapes_change()
        proxy_ranges = zip((0, *change_indices), (*change_indices, len(flat_data.proxies)))
        days = set()
        copy_number = 0
        for s, e in proxy_ranges:
            proxies = flat_data.proxies[s:e]
            if proxies:
                p = flat_data.create_proxy()
                p.proxies.extend(proxies)
                if p.shape[1] == len(self.channel_names):
                    n_days = (p.end_datetime - p.start_datetime).days + 1
                    first_date = p.start_datetime.date()
                    signal_headers = make_signal_headers(
                        self.channel_names,
                        sample_frequency=p.sample_rate,
                        physical_min=-1000000.0,
                        physical_max=320000.0,
                    )
                    for d in range(n_days):
                        # Generate date and file path
                        date = first_date + datetime.timedelta(days=d)
                        if date in days:
                            copy_number += 1
                        else:
                            days.add(first_date + datetime.timedelta(days=d))
                            copy_number = 0

                        file_name = f"{name}_task-day{len(days)}{'' if copy_number == 0 else f'_{copy_number}'}.edf"
                        file_path = path / file_name

                        if not file_path.is_file():
                            # Get Data
                            day_data = p.find_data_range(
                                start=first_date + datetime.timedelta(days=d),
                                stop=first_date + datetime.timedelta(days=d+1),
                                approx=True,
                                tails=True,
                                dtype="f4"
                            )
                            edf_header["startdate"] = day_data.data.start_datetime

                            # Fill missing data with fill_value
                            if fill:
                                times = day_data.axis.timestamps - day_data.axis.start_timestamp
                                invalidity = day_data.data[:, 0] == self.fill_value
                                edges = np.roll(invalidity, 1) != invalidity
                                edges[0] = invalidity[0]
                                indices = np.where(edges)[0]
                                n_indices = len(indices)

                                annotations = []
                                for temp_s_index in range(n_indices//2):
                                    s_index = indices[temp_s_index * 2]
                                    e_index = indices[temp_s_index * 2 + 1]
                                    invalid_start = times[s_index]
                                    invalid_duration = times[e_index] - invalid_start
                                    annotations.append((invalid_start, invalid_duration, "Invalid Time"))

                                if (n_indices % 2) != 0:
                                    invalid_start = times[indices[-1]]
                                    invalid_duration = times[-1] - invalid_start
                                    annotations.append((invalid_start, invalid_duration, "Invalid Time"))

                                edf_header["annotations"] = annotations

                            # Save and Clear
                            self.formated_save_edf(
                                path=file_path,
                                signals=day_data.data.data.T,
                                signal_headers=signal_headers,
                                header=edf_header,
                            )
                            del day_data
                            gc.collect()


