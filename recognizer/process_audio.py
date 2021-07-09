import pickle

import wave
import python_speech_features as ps

import numpy as np


def extract_features(audio_file, **kwargs):

    def _load_data():
        with open('./recognizer/stats/zscore40.pkl', 'rb') as f:
            mean1, std1, mean2, std2, mean3, std3 = pickle.load(f)
        return mean1, std1, mean2, std2, mean3, std3

    def _read_file(audio_file_path):
        file = wave.open(audio_file_path, 'r')
        params = file.getparams()

        nchannels, sampwidth, framerate, wav_length = params[:4]
        str_data = file.readframes(wav_length)
        wavedata = np.fromstring(str_data, dtype=np.short)
        time = np.arange(0, wav_length) * (1.0/framerate)

        file.close()

        return wavedata, time, framerate

    mean1, std1, mean2, std2, mean3, std3 = _load_data()

    # Dataset parameters
    dataset_size = 0
    filter_num = 40
    eps = 1e-5

    dataset = np.zeros((1, 300, filter_num, 3), dtype=np.float32)

    # Calulate log-Mel Spectrum for audio file
    data, time, rate = _read_file(audio_file)
    mel_spec = ps.logfbank(data, rate, nfilt=40)
    delta1 = ps.delta(mel_spec, 2)
    delta2 = ps.delta(delta1, 2)

    time = mel_spec.shape[0]

    if(time <= 300):
        part = mel_spec
        delta11 = delta1
        delta21 = delta2

        part = np.pad(
            part, ((0, 300 - part.shape[0]), (0, 0)), 'constant', constant_values=0)
        delta11 = np.pad(
            delta11, ((0, 300 - delta11.shape[0]), (0, 0)), 'constant', constant_values=0)
        delta21 = np.pad(
            delta21, ((0, 300 - delta21.shape[0]), (0, 0)), 'constant', constant_values=0)

        dataset[dataset_size, :, :, 0] = (part - mean1)/(std1+eps)
        dataset[dataset_size, :, :, 1] = (delta11 - mean2)/(std2+eps)
        dataset[dataset_size, :, :, 2] = (delta21 - mean3)/(std3+eps)

        dataset_size += 1

    else:
        for i in range(1):
            if(i == 0):
                begin = 0
                end = begin + 300
            else:
                begin = time - 300
                end = time

            part = mel_spec[begin:end, :]
            delta11 = delta1[begin:end, :]
            delta21 = delta2[begin:end, :]

            dataset[dataset_size, :, :, 0] = (part - mean1)/(std1+eps)
            dataset[dataset_size, :, :, 1] = (delta11 - mean2)/(std2+eps)
            dataset[dataset_size, :, :, 2] = (delta21 - mean3)/(std3+eps)

            dataset_size += 1

    return dataset
