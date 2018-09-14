#!/usr/bin/env python3

import glob
import os
import subprocess
import sys

import numpy as np
from scipy.io import wavfile
from scipy.signal import correlate, find_peaks

episodes_filepaths = sys.argv[1:]

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
SOUND_SUBDIR = os.path.join(OUTPUT_DIR, 'sound')
SOUND_EDITED_SUBDIR = os.path.join(OUTPUT_DIR, 'sound_edited')
EPISODE_EDITED_SUBDIR = os.path.join(OUTPUT_DIR, 'episodes_edited')

SAMPLING_RATE = 48000  # N.B. use this to resample excerpts: ffmpeg -i excerpt.wav -ar 48000 excerpt_48000.wav


def nparray_from_wav(wav_filepath):
    rate, nparray = wavfile.read(wav_filepath)

    return np.array(nparray, dtype=np.float64), rate


def find_timings(episode_sound, excerpt_sound, min_timing_relative, max_timing_relative):
    correlation = correlate(episode_sound, excerpt_sound, 'valid', 'fft')

    correlation = np.array(correlation.flatten(), dtype=np.float64)  # find_peaks needs a 1-dimensional array

    distance_in_seconds = 5
    height_relative = 0.5
    peaks, _ = find_peaks(correlation,
                          distance=int(distance_in_seconds * SAMPLING_RATE),
                          height=int(height_relative * np.max(correlation)))

    episode_len = len(episode_sound)
    min_timing_samples = int(min_timing_relative * episode_len)
    max_timing_samples = int(max_timing_relative * episode_len)

    peaks_filtered = peaks[peaks >= min_timing_samples]
    peaks_filtered = peaks_filtered[peaks_filtered <= max_timing_samples]

    # debug
    #
    # print peaks
    # print min_timing_samples, max_timing_samples
    # print peaks_filtered
    #
    # plt.plot(correlation)
    # plt.plot(peaks, correlation[peaks], "X")
    # plt.plot(peaks_filtered, correlation[peaks_filtered], "o")
    # plt.show()

    return peaks_filtered


for episode_filepath in sorted(episodes_filepaths):
    episode_filename = os.path.basename(episode_filepath)

    print(u"episode: " + episode_filepath)

    episode_edited_filepath = os.path.join(EPISODE_EDITED_SUBDIR, episode_filename)
    episode_sound_filepath = os.path.join(SOUND_SUBDIR, episode_filename.replace("mkv", "wav"))
    episode_sound_edited_filepath = os.path.join(SOUND_EDITED_SUBDIR, episode_filename.replace(".mkv", ".wav"))

    # extract audio

    # TODO use ffmpeg-python
    # stream = ffmpeg.input('').output('', ar=SAMPLING_RATE)
    # ffmpeg.run(stream)
    subprocess.call(
        ['ffmpeg', '-i', episode_filepath, '-ar', str(SAMPLING_RATE), '-y', episode_sound_filepath],
        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    episode_sound, episode_sound_rate = nparray_from_wav(episode_sound_filepath)

    if episode_sound_rate != SAMPLING_RATE:
        print("unexpected episode sampling rate (is %s, should be %s)" % (episode_sound_rate, SAMPLING_RATE))
        exit(1)

    # find sections to mute in extracted audio

    sections_to_mute = []

    for excerpt_filename, min_timing_relative, max_timing_relative, cut_before_seconds, cut_after_seconds in [
        ("horn_48000.wav", 0, 0.05, 0, 2.8),
        ("music_48000.wav", 0, 0.3, 0, 6.2),
        ("music_end_48000.wav", 0.7, 1, 0, 4.2),
        ("end_48000.wav", 0.8, 1, 0, 1.53)]:
        print("excerpt: " + excerpt_filename)

        excerpt, excerpt_rate = nparray_from_wav(os.path.join(OUTPUT_DIR, excerpt_filename))

        if excerpt_rate != SAMPLING_RATE:
            print("unexpected excerpt sampling rate (is %s, should be %s)" % (excerpt_rate, SAMPLING_RATE))
            exit(1)

        timings = find_timings(episode_sound, excerpt, min_timing_relative, max_timing_relative)

        if len(timings) == 0:
            print("no timing found")
            continue

        if len(timings) > 1:
            print("multiple timings found: %s" % len(timings))

        timing = timings[0]

        sections_to_mute.append(
            (max(0, timing - int(cut_before_seconds * SAMPLING_RATE)),
             min(len(episode_sound) - 1, timing + int(cut_after_seconds * SAMPLING_RATE))))

    # mute relevant sections

    if not sections_to_mute:
        print("no section to mute")
        continue

    episode_edited = np.array(episode_sound.copy(), dtype=np.int16)  # episode is read-only
    for start, end in sections_to_mute:
        episode_edited[start:end] = 0

    wavfile.write(episode_sound_edited_filepath, SAMPLING_RATE, episode_edited)

    # generate video file with alternative audio

    # TODO use ffmpeg-python
    subprocess.call(
        ['ffmpeg', '-i', episode_filepath, '-i', episode_sound_edited_filepath,
        '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0',
        '-y', episode_edited_filepath],
        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)

    # clean temporary files

    for filepath in glob.glob(os.path.join(SOUND_SUBDIR, "*.wav")) + glob.glob(os.path.join(SOUND_EDITED_SUBDIR, "*.wav")):
        print("delete " + filepath)
        os.remove(filepath)
