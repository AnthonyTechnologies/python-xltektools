"""
.. _basics:

NWB File Basics
===============

This example will focus on the basics of working with an :py:class:`~pynwb.file.NWBFile` object,
including writing and reading of an NWB file, and giving you an introduction to the basic data types.
Before we dive into code showing how to use an :py:class:`~pynwb.file.NWBFile`, we first provide
a brief overview of the basic concepts of NWB. If you are already familiar with the concepts of
:ref:`timeseries_overview` and :ref:`modules_overview`, then feel free to skip the :ref:`basics_background`
part and go directly to :ref:`basics_nwbfile`.

.. _basics_background:

Background: Basic concepts
--------------------------

In the `NWB Format <https://nwb-schema.readthedocs.io>`_, each experimental session is typically
represented by a separate NWB file. NWB files are represented in PyNWB by :py:class:`~pynwb.file.NWBFile`
objects which provide functionality for creating and retrieving:

 * :ref:`timeseries_overview` datasets, i.e., objects for storing time series data
 * :ref:`modules_overview`, i.e., objects for storing and grouping analyses, and
 * experimental metadata and other metadata related to data provenance.

The following sections describe the :py:class:`~pynwb.base.TimeSeries` and :py:class:`~pynwb.base.ProcessingModules`
classes in further detail.

.. _timeseries_overview:

TimeSeries
^^^^^^^^^^

:py:class:`~pynwb.base.TimeSeries` objects store time series data and correspond to the *TimeSeries* specifications
provided by the `NWB Format`_ . Like the NWB specification, :py:class:`~pynwb.base.TimeSeries` Python objects
follow an object-oriented inheritance pattern, i.e., the class :py:class:`~pynwb.base.TimeSeries`
serves as the base class for all other :py:class:`~pynwb.base.TimeSeries` types, such as,
:py:class:`~pynwb.ecephys.ElectricalSeries`, which itself may have further subtypes, e.g.,
:py:class:`~pynwb.ecephys.SpikeEventSeries`.

.. seealso::

    For your reference, NWB defines the following main :py:class:`~pynwb.base.TimeSeries` subtypes:

    * **Extracellular electrophysiology:**
      :py:class:`~pynwb.ecephys.ElectricalSeries`, :py:class:`~pynwb.ecephys.SpikeEventSeries`

    * **Intracellular electrophysiology:**
      :py:class:`~pynwb.icephys.PatchClampSeries` is the base type for all intracellular time series, which
      is further refined into subtypes depending on the type of recording:
      :py:class:`~pynwb.icephys.CurrentClampSeries`,
      :py:class:`~pynwb.icephys.IZeroClampSeries`,
      :py:class:`~pynwb.icephys.CurrentClampStimulusSeries`,
      :py:class:`~pynwb.icephys.VoltageClampSeries`,
      :py:class:`~pynwb.icephys.VoltageClampStimulusSeries`.

    * **Optical physiology and imaging:** :py:class:`~pynwb.image.ImageSeries` is the base type
      for image recordings and is further refined by the
      :py:class:`~pynwb.image.ImageMaskSeries`,
      :py:class:`~pynwb.image.OpticalSeries`, and
      :py:class:`~pynwb.ophys.TwoPhotonSeries` types.
      Other related time series types are:
      :py:class:`~pynwb.image.IndexSeries` and
      :py:class:`~pynwb.ophys.RoiResponseSeries`.

    * **Others** :py:class:`~pynwb.ogen.OptogeneticSeries`,
      :py:class:`~pynwb.behavior.SpatialSeries`,
      :py:class:`~pynwb.misc.DecompositionSeries`,
      :py:class:`~pynwb.misc.AnnotationSeries`,
      :py:class:`~pynwb.misc.AbstractFeatureSeries`, and
      :py:class:`~pynwb.misc.IntervalSeries`.


.. _modules_overview:

Processing Modules
^^^^^^^^^^^^^^^^^^

Processing modules are objects that group together common analyses done during processing of data.
Processing module objects are unique collections of analysis results. To standardize the storage of
common analyses, NWB provides the concept of an :py:class:`~pynwb.core.NWBDataInterface`, where the output of
common analyses are represented as objects that extend the :py:class:`~pynwb.core.NWBDataInterface` class.
In most cases, you will not need to interact with the :py:class:`~pynwb.core.NWBDataInterface` class directly.
More commonly, you will be creating instances of classes that extend this class.


.. seealso::

    For your reference, NWB defines the following main analysis :py:class:`~pynwb.core.NWBDataInterface` subtypes:

    * **Behavior:** :py:class:`~pynwb.behavior.BehavioralEpochs`,
      :py:class:`~pynwb.behavior.BehavioralEvents`,
      :py:class:`~pynwb.behavior.BehavioralTimeSeries`,
      :py:class:`~pynwb.behavior.CompassDirection`,
      :py:class:`~pynwb.behavior.PupilTracking`,
      :py:class:`~pynwb.behavior.Position`,
      :py:class:`~pynwb.behavior.EyeTracking`.

    * **Extracellular electrophysiology:** :py:class:`~pynwb.ecephys.EventDetection`,
      :py:class:`~pynwb.ecephys.EventWaveform`,
      :py:class:`~pynwb.ecephys.FeatureExtraction`,
      :py:class:`~pynwb.ecephys.FilteredEphys`,
      :py:class:`~pynwb.ecephys.LFP`.

    * **Optical physiology:** :py:class:`~pynwb.ophys.DfOverF`,
      :py:class:`~pynwb.ophys.Fluorescence`,
      :py:class:`~pynwb.ophys.ImageSegmentation`,
      :py:class:`~pynwb.ophys.MotionCorrection`.

    * **Others:** :py:class:`~pynwb.retinotopy.ImagingRetinotopy`,
      :py:class:`~pynwb.base.Images`.

    * **TimeSeries:** Any :ref:`timeseries_overview` is also a subclass of :py:class:`~pynwb.core.NWBDataInterface`
      and can be used anywhere :py:class:`~pynwb.core.NWBDataInterface` is allowed.

.. note::

    In addition to :py:class:`~pynwb.core.NWBContainer`, which functions as a common base type for Group objects,
    :py:class:`~pynwb.core.NWBData` provides a common base for the specification of datasets in the NWB format.

The following examples will reference variables that may not be defined within the block they are used in. For
clarity, we define them here:
"""
# sphinx_gallery_thumbnail_path = 'figures/gallery_thumbnails_file.png'
import numpy as np
from pynwb import NWBFile, TimeSeries, NWBHDF5IO
from pynwb.epoch import TimeIntervals
from pynwb.file import Subject
from pynwb.behavior import SpatialSeries, Position
from datetime import datetime
from dateutil import tz
from hdmf.backends.hdf5.h5_utils import H5DataIO

####################
# .. _basics_nwbfile:
#
# The NWB file
# ------------
#
# An :py:class:`~pynwb.file.NWBFile` represents a single session of an experiment.
# Each :py:class:`~pynwb.file.NWBFile` must have a session description, identifier, and session start time.
# Importantly, the session start time is the reference time for all timestamps in the file.
# For instance, an event with a timestamp of 0 in the file means the event
# occurred exactly at the session start time.
#
# Create an :py:class:`~pynwb.file.NWBFile` object with the required fields
# (``session_description``, ``identifier``, ``session_start_time``) and additional metadata.
#
# .. note::
#     Use keyword arguments when constructing :py:class:`~pynwb.file.NWBFile` objects.
#

session_start_time = datetime(2018, 4, 25, 2, 30, 3, tzinfo=tz.gettz("US/Pacific"))

nwbfile = NWBFile(
    session_description="Mouse exploring an open field",  # required
    identifier="Mouse5_Day3",  # required
    session_start_time=session_start_time,  # required
    session_id="session_1234",  # optional
    experimenter="My Name",  # optional
    lab="My Lab Name",  # optional
    institution="University of My Institution",  # optional
    related_publications="DOI:10.1016/j.neuron.2016.12.011",  # optional
)
print(nwbfile)

####################
# .. _basic_subject:
#
# Subject Information
# -------------------
#
# In the :py:class:`~pynwb.file.Subject` object we can store information about the experimental subject,
# such as ``age``, ``species``, ``genotype``, ``sex``, and a ``description``.
#
# .. only:: html
#
#   .. image:: ../../_static/Subject.svg
#     :width: 150
#     :alt: subject UML diagram
#     :align: center
#
# .. only:: latex
#
#   .. image:: ../../_static/Subject.png
#     :width: 150
#     :alt: subject UML diagram
#     :align: center
#
# The fields in the :py:class:`~pynwb.file.Subject` object are all free-form text (any format will be valid),
# however it is recommended to follow particular conventions to help software tools interpret the data:
#
# * **age**: `ISO 8601 Duration format <https://en.wikipedia.org/wiki/ISO_8601#Durations>`_, e.g., ``"P90D"`` for 90 days old
# * **species**: The formal latin binomial nomenclature, e.g., ``"Mus musculus"``, ``"Homo sapiens"``
# * **sex**: Single letter abbreviation, e.g., ``"F"`` (female), ``"M"`` (male), ``"U"`` (unknown), and ``"O"`` (other)
#
# Add the subject information to the :py:class:`~pynwb.file.NWBFile`
# by setting the ``subject`` field to the new :py:class:`~pynwb.file.Subject` object.

nwbfile.subject = Subject(
    subject_id="001",
    age="P90D",
    description="mouse 5",
    species="Mus musculus",
    sex="M",
)

####################
# .. _basic_timeseries:
#
# Time Series Data
# ----------------
#
# :py:class:`~pynwb.base.TimeSeries` is a common base class for measurements sampled over time,
# and provides fields for ``data`` and ``timestamps`` (regularly or irregularly sampled).
# You will also need to supply the ``name`` and ``unit`` of measurement
# (`SI unit <https://en.wikipedia.org/wiki/International_System_of_Units>`_).
#
# .. image:: ../../_static/TimeSeries.png
#   :width: 200
#   :alt: timeseries UML diagram
#   :align: center
#
# For instance, we can store a :py:class:`~pynwb.base.TimeSeries` data where recording started
# ``0.0`` seconds after ``start_time`` and sampled every second:

data = list(range(100, 200, 10))
time_series_with_rate = TimeSeries(
    name="test_timeseries",
    data=data,
    unit="m",
    starting_time=0.0,
    rate=1.0,
)

####################
# For irregularly sampled recordings, we need to provide the ``timestamps`` for the ``data``:

data = H5DataIO(
    data=np.array([[1.0]]),
    maxshape=(None, 1),  # <-- Make the time dimension resizable
    compression='gzip',   # <-- Enable GZip compression
    compression_opts=4,   # <-- GZip aggression
    shuffle=True,         # <-- Enable shuffle filter
    fillvalue=np.nan,     # <-- Use NAN as fillvalue
)
timestamps = H5DataIO(
    data=np.array([0], dtype=np.uint64),
    maxshape=(None, ),  # <-- Make the time dimension resizable
    compression='gzip',   # <-- Enable GZip compression
    compression_opts=4,   # <-- GZip aggression
    shuffle=True,         # <-- Enable shuffle filter
    fillvalue=0,     # <-- Use NAN as fillvalue
)
time_series_with_timestamps = TimeSeries(
    name="test_timeseries",
    data=data,
    unit="m",
    timestamps=timestamps,
)

####################
# :py:class:`~pynwb.base.TimeSeries` objects can be added directly to :py:class:`~pynwb.file.NWBFile` using:
#
# * :py:meth:`~pynwb.file.NWBFile.add_acquisition` to  add *acquisition* data (raw, acquired data that should never change),
# * :py:meth:`~pynwb.file.NWBFile.add_stimulus` to add *stimulus* data, or
# * :py:meth:`~pynwb.file.NWBFile.add_stimulus_template` to store *stimulus templates*.
#

nwbfile.add_acquisition(time_series_with_timestamps)

####################
# We can access the :py:class:`~pynwb.base.TimeSeries` object ``'test_timeseries'``
# in :py:class:`~pynwb.file.NWBFile` from ``acquisition``:

nwbfile.acquisition["test_timeseries"]

####################
# or using the :py:meth:`~pynwb.file.NWBFile.get_acquisition` method:
nwbfile.get_acquisition("test_timeseries")

####################
# .. _basic_writing:
#
# Writing an NWB file
# -------------------
#
# NWB I/O is carried out using the :py:class:`~pynwb.NWBHDF5IO` class [#]_. This class is responsible
# for mapping an :py:class:`~pynwb.file.NWBFile` object into HDF5 according to the NWB schema.
#
# To write an :py:class:`~pynwb.file.NWBFile`, use the :py:meth:`~hdmf.backends.io.HDMFIO.write` method.

io = NWBHDF5IO("basics_tutorial.nwb", mode="w")
io.write(nwbfile)
io.close()

