"""xltekcdfsedfexporter.py
A HDF5 file which contains data for XLTEK EEG data.
"""
# Package Header #
from ..header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from collections.abc import Iterable
from copy import deepcopy
import datetime
import gc
from pathlib import Path
import traceback
from typing import Any

# Third-Party Packages #
from baseobjects import BaseObject
from proxyarrays import BlankTimeProxy
import numpy as np
from pyedflib import FILETYPE_BDFPLUS
from pyedflib import FILETYPE_EDFPLUS
from pyedflib import EdfWriter
from pyedflib.highlevel import make_header
from pyedflib.highlevel import make_signal_headers

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

    def _write_proxy_samples(self, writer, data, start=None, stop=None, digital=False):
        """ """
        samples_step = writer.get_smp_per_record(0)
        dtype = np.int32 if digital else np.float64

        for record in data.islices(samples_step, slice(start, stop), dtype=dtype, proxy=False):
            if record.shape[0] < samples_step:
                old_record = record
                record = np.zeros(shape=(samples_step, old_record.shape[1]), dtype=dtype)
                record[: old_record.shape[0], :] = old_record

            if digital:
                success = writer.blockWriteDigitalSamples(record.T.flatten())
            else:
                success = writer.blockWritePhysicalSamples(record.T.flatten())

            if success < 0:
                raise OSError(f"Unknown error while calling blockWriteSamples: {success}")

    def write_edf_proxy(
        self,
        path: Path,
        signals: np.ndarray,
        signal_headers: list[dict[str, Any]],
        header: dict[str, Any] | None = None,
        start: Any = None,
        stop: Any = None,
        digital: bool = False,
        file_type: str | None = None,
    ):
        """ """
        assert len(signal_headers) == signals.shape[1], "signals and signal_headers must be same length"

        header = make_header() | ({} if header is None else header)
        annotations = header.get("annotations", [])
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

        with EdfWriter(path.as_posix(), n_channels=signals.shape[1], file_type=file_type) as f:
            f.setSignalHeaders(signal_headers)
            f.setHeader(header)
            self._write_proxy_samples(writer=f, data=signals, start=start, stop=stop, digital=digital)
            for annotation in annotations:
                f.writeAnnotation(*annotation)
        del f

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
        info = self.cdfs.components["meta_information"].get_meta_information()
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
                            stop=first_hour + datetime.timedelta(days=h + 1),
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

    def export_as_days(self, path: Path, name: str | None = None, fill: bool = True) -> None:
        # Get Name and Create Header
        name = self.new_name if name is None else name
        edf_header = self.create_header()

        # Flatten Data
        proxy = self.cdfs.components["contents"].require_contents_proxy()
        flat_data = proxy.as_flattened()
        if not self.cdfs:
            print(
                f"self.cdfs is not defined when it should be. export cannot be performed. self.cdsf value: {self.cdfs}"
            )
            return
        try:
            sample_frequency = 1 / flat_data.sample_period
            print(f"sample frequency: {sample_frequency}")
        except IndexError as e:
            print("The following index error was raised:")
            traceback.print_exc()
            print(f"Unable to access sample period, export cannot be performed. flat_data value: {flat_data}")
            return

        # Fill Missing Data
        if fill:
            flat_data.time_tolerance = flat_data.sample_period
            flat_data.insert_missing(fill_method="full", fill_kwargs={"fill_value": self.fill_value})

        # Get Ranges of Proxies of Same Shape/Channel Count
        change_indices = flat_data.where_shapes_change()
        proxy_ranges = zip((0, *change_indices), (*change_indices, len(flat_data.proxies)))

        # Loop Over Proxy Ranges
        days = set()
        copy_number = 0
        for s, e in proxy_ranges:
            proxies = flat_data.proxies[s:e]
            if proxies:
                proxy_segment = flat_data.create_return_proxy()
                proxy_segment.proxies.extend(proxies)

                if proxy_segment.shape[1] != len(self.channel_names):
                    print(f"The shape of the proxy does not match the length of the channels. export impossible")
                    print(f"proxy: {proxy_segment}")
                    print(f"proxy length: {proxy_segment.shape[1]}")
                    print(f"channel length: {len(self.channel_names)}")
                    continue
                # Only Export Proxy Ranges that Match the Channels
                if proxy_segment.shape[1] == len(self.channel_names):
                    # Create Signal Headers
                    signal_headers = make_signal_headers(
                        self.channel_names,
                        sample_frequency=proxy_segment.sample_rate,
                        physical_min=-1000000.0,
                        physical_max=320000.0,
                    )

                    # Get Starts of Blank/Fill Data
                    blank_indices = np.where(tuple(isinstance(proxy, BlankTimeProxy) for proxy in proxy_segment))[0]
                    blank_starts = np.fromiter((proxy_segment.proxy_start_indices[i] for i in blank_indices), dtype=int)

                    # Loop Over and Export Days
                    n_days = (proxy_segment.end_date - proxy_segment.start_date).days + 1
                    first_date = proxy_segment.start_datetime.date()
                    for d in range(n_days):
                        print(f"Exporting day {d + 1}...")
                        # Generate Date and File path
                        date = first_date + datetime.timedelta(days=d)
                        if date in days:
                            copy_number += 1
                        else:
                            days.add(first_date + datetime.timedelta(days=d))
                            copy_number = 0

                        file_name = (
                            f"{name}_task-day{len(days)}_ieeg{'' if copy_number == 0 else f'_{copy_number}'}.edf"
                        )
                        file_path = path / file_name

                        # Export to Non-Existing Files
                        if not file_path.is_file():
                            # Get Data Slices Indices
                            start_index, stop_index, _ = proxy_segment.find_time_index_slice(
                                start=first_date + datetime.timedelta(days=d),
                                stop=first_date + datetime.timedelta(days=d + 1),
                                approx=True,
                                tails=True,
                            )
                            edf_header["startdate"] = start_index.datetime

                            # Create Annotations with Blank/Fill Information
                            if fill:
                                valid_blanks = (start_index[0] < blank_starts) == (blank_starts < stop_index[0])
                                annotations = []
                                for index in blank_indices[valid_blanks]:
                                    proxy = proxy_segment.proxies[index]
                                    invalid_start = proxy.start_timestamp - start_index.datetime.timestamp()
                                    invalid_duration = proxy.end_timestamp - proxy.start_timestamp
                                    annotations.append((invalid_start, invalid_duration, "Invalid Time"))

                                edf_header["annotations"] = annotations

                            # Save and Clear
                            self.write_edf_proxy(
                                path=file_path,
                                signals=proxy_segment,
                                signal_headers=signal_headers,
                                start=start_index[0],
                                stop=stop_index[0],
                                header=edf_header,
                            )
                            proxy_segment.clear_all_caches()
                            gc.collect()
