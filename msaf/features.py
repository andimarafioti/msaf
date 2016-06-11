"""
MSAF module with the available features.

Each feature must inherit from the base class `Features` to be
included in the whole framework.
"""

from builtins import super
import librosa
import numpy as np

# Local stuff
import msaf
from msaf import utils
from msaf import config
from msaf.input_output import FileStruct
from msaf.base import Features


class CQT(Features):
    """This class contains the implementation of the Constant-Q Transform.

    These features contain both harmonic and timbral content of the given
    audio signal.
    """
    def __init__(self, file_struct, feat_type, sr=msaf.Anal.sample_rate,
                 hop_length=msaf.Anal.hop_size, n_bins=msaf.Anal.cqt_bins,
                 norm=msaf.Anal.cqt_norm,
                 filter_scale=msaf.Anal.cqt_filter_scale, ref_power=np.max):
        """Constructor of the class.

        Parameters
        ----------
        file_struct: `msaf.input_output.FileStruct`
            Object containing the file paths from where to extract/read
            the features.
        feat_type: `FeatureTypes`
            Enum containing the type of features.
        sr: int > 0
            Sampling rate for the analysis.
        hop_length: int > 0
            Hop size in frames for the analysis.
        n_bins: int > 0
            Number of frequency bins for the CQT.
        norm: float
            Type of norm to use for basis function normalization.
        filter_scale: float
            The scale of the filter for the CQT.
        ref_power: function
            The reference power for logarithmic scaling.
        """
        # Init the parent
        super().__init__(file_struct=file_struct, sr=sr, hop_length=hop_length,
                         feat_type=feat_type)
        # Init the CQT parameters
        self.n_bins = n_bins
        self.norm = norm
        self.filter_scale = filter_scale
        self.ref_power = ref_power

    @classmethod
    def get_id(self):
        """Identifier of these features."""
        return "cqt"

    def compute_features(self):
        """Actual implementation of the features.

        Returns
        -------
        cqt: np.array(N, F)
            The features, each row representing a feature vector for a give
            time frame/beat.
        """
        linear_cqt = np.abs(librosa.cqt(
            self._audio, sr=self.sr, hop_length=self.hop_length,
            n_bins=self.n_bins, norm=self.norm, filter_scale=self.filter_scale,
            real=False)) ** 2
        cqt = librosa.logamplitude(linear_cqt, ref_power=self.ref_power).T
        return cqt


class MFCC(Features):
    """This class contains the implementation of the MFCC Features.

    The Mel-Frequency Cepstral Coefficients contain timbral content of a
    given audio signal.
    """
    def __init__(self, file_struct, feat_type, sr=msaf.Anal.sample_rate,
                 hop_length=msaf.Anal.hop_size, n_fft=msaf.Anal.n_fft,
                 n_mels=msaf.Anal.n_mels, n_mfcc=msaf.Anal.n_mfcc,
                 ref_power=np.max):
        """Constructor of the class.

        Parameters
        ----------
        file_struct: `msaf.input_output.FileStruct`
            Object containing the file paths from where to extract/read
            the features.
        feat_type: `FeatureTypes`
            Enum containing the type of features.
        sr: int > 0
            Sampling rate for the analysis.
        hop_length: int > 0
            Hop size in frames for the analysis.
        n_fft: int > 0
            Number of frames for the FFT.
        n_mels: int > 0
            Number of mel filters.
        n_mfcc: int > 0
            Number of mel coefficients.
        ref_power: function
            The reference power for logarithmic scaling.
        """
        # Init the parent
        super().__init__(file_struct=file_struct, sr=sr, hop_length=hop_length,
                         feat_type=feat_type)
        # Init the MFCC parameters
        self.n_fft = n_fft
        self.n_mels = n_mels
        self.n_mfcc = n_mfcc
        self.ref_power = ref_power

    @classmethod
    def get_id(self):
        """Identifier of these features."""
        return "mfcc"

    def compute_features(self):
        """Actual implementation of the features.

        Returns
        -------
        mfcc: np.array(N, F)
            The features, each row representing a feature vector for a give
            time frame/beat.
        """
        S = librosa.feature.melspectrogram(self._audio,
                                           sr=self.sr,
                                           n_fft=self.n_fft,
                                           hop_length=self.hop_length,
                                           n_mels=self.n_mels)
        log_S = librosa.logamplitude(S, ref_power=self.ref_power)
        mfcc = librosa.feature.mfcc(S=log_S, n_mfcc=self.n_mfcc).T
        return mfcc


class PCP(Features):
    """This class contains the implementation of the Pitch Class Profiles.

    The PCPs contain harmonic content of a given audio signal.
    """
    def __init__(self, file_struct, feat_type, sr=msaf.Anal.sample_rate,
                 hop_length=msaf.Anal.hop_size, n_bins=msaf.Anal.cqt_bins,
                 norm=msaf.Anal.cqt_norm, f_min=msaf.Anal.f_min,
                 n_octaves=msaf.Anal.n_octaves):
        """Constructor of the class.

        Parameters
        ----------
        file_struct: `msaf.input_output.FileStruct`
            Object containing the file paths from where to extract/read
            the features.
        feat_type: `FeatureTypes`
            Enum containing the type of features.
        sr: int > 0
            Sampling rate for the analysis.
        hop_length: int > 0
            Hop size in frames for the analysis.
        n_bins: int > 0
            Number of bins for the CQT computation.
        norm: int > 0
            Normalization parameter.
        f_min: float > 0
            Minimum frequency.
        n_octaves: int > 0
            Number of octaves.
        """
        # Init the parent
        super().__init__(file_struct=file_struct, sr=sr, hop_length=hop_length,
                         feat_type=feat_type)
        # Init the PCP parameters
        self.n_bins = n_bins
        self.norm = norm
        self.f_min = f_min
        self.n_octaves = n_octaves

    @classmethod
    def get_id(self):
        """Identifier of these features."""
        return "pcp"

    def compute_features(self):
        """Actual implementation of the features.

        Returns
        -------
        pcp: np.array(N, F)
            The features, each row representing a feature vector for a give
            time frame/beat.
        """
        audio_harmonic, _ = self.compute_HPSS()
        pcp_cqt = np.abs(librosa.hybrid_cqt(audio_harmonic,
                                            sr=self.sr,
                                            hop_length=self.hop_length,
                                            n_bins=self.n_bins,
                                            norm=self.norm,
                                            fmin=self.f_min)) ** 2
        pcp = librosa.feature.chroma_cqt(C=pcp_cqt,
                                         sr=self.sr,
                                         hop_length=self.hop_length,
                                         n_octaves=self.n_octaves,
                                         fmin=self.f_min).T
        return pcp


class Tonnetz(Features):
    """This class contains the implementation of the Tonal Centroids.

    The Tonal Centroids (or Tonnetz) contain harmonic content of a given audio
    signal.
    """
    def __init__(self, file_struct, feat_type, sr=msaf.Anal.sample_rate,
                 hop_length=msaf.Anal.hop_size, n_bins=msaf.Anal.cqt_bins,
                 norm=msaf.Anal.cqt_norm, f_min=msaf.Anal.f_min,
                 n_octaves=msaf.Anal.n_octaves):
        """Constructor of the class.

        Parameters
        ----------
        file_struct: `msaf.input_output.FileStruct`
            Object containing the file paths from where to extract/read
            the features.
        feat_type: `FeatureTypes`
            Enum containing the type of features.
        sr: int > 0
            Sampling rate for the analysis.
        hop_length: int > 0
            Hop size in frames for the analysis.
        n_bins: int > 0
            Number of bins for the CQT computation.
        norm: int > 0
            Normalization parameter.
        f_min: float > 0
            Minimum frequency.
        n_octaves: int > 0
            Number of octaves.
        """
        # Init the parent
        super().__init__(file_struct=file_struct, sr=sr, hop_length=hop_length,
                         feat_type=feat_type)
        # Init the local parameters
        self.n_bins = n_bins
        self.norm = norm
        self.f_min = f_min
        self.n_octaves = n_octaves

    @classmethod
    def get_id(self):
        """Identifier of these features."""
        return "tonnetz"

    def compute_features(self):
        """Actual implementation of the features.

        Returns
        -------
        tonnetz: np.array(N, F)
            The features, each row representing a feature vector for a give
            time frame/beat.
        """
        pcp = PCP(self.file_struct, self.feat_type, self.sr, self.hop_length,
                  self.n_bins, self.norm, self.f_min, self.n_octaves).features
        tonnetz = librosa.feature.tonnetz(chroma=pcp)
        return tonnetz


class Tempogram(Features):
    """This class contains the implementation of the Tempogram feature.

    The Tempogram contains rhythmic content of a given audio signal.
    """
    def __init__(self, file_struct, feat_type, sr=msaf.Anal.sample_rate,
                 hop_length=msaf.Anal.hop_size,
                 win_length=msaf.Anal.win_length):
        """Constructor of the class.

        Parameters
        ----------
        file_struct: `msaf.input_output.FileStruct`
            Object containing the file paths from where to extract/read
            the features.
        feat_type: `FeatureTypes`
            Enum containing the type of features.
        sr: int > 0
            Sampling rate for the analysis.
        hop_length: int > 0
            Hop size in frames for the analysis.
        win_length: int > 0
            The size of the window for the tempogram.
        """
        # Init the parent
        super().__init__(file_struct=file_struct, sr=sr, hop_length=hop_length,
                         feat_type=feat_type)
        # Init the local parameters
        self.win_length = win_length

    @classmethod
    def get_id(self):
        """Identifier of these features."""
        return "tempogram"

    def compute_features(self):
        """Actual implementation of the features.

        Returns
        -------
        tempogram: np.array(N, F)
            The features, each row representing a feature vector for a give
            time frame/beat.
        """
        return librosa.feature.tempogram(self._audio, sr=self.sr,
                                         hop_length=self.hop_length,
                                         win_length=self.win_length).T
