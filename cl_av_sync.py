#!/usr/local/bin/python
# -*- coding: utf-8 -*-
# @Author  : Noel
import click
import cv2 as cv
import numpy as np
import subprocess
import datetime
from scipy import stats
from scipy.io import wavfile
import json
import time

from Common import *


class AVSync(object):
    def __init__(self, result_name):
        super(AVSync, self).__init__()
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.result_name = cur_time + '_' + result_name
        self.tmp_file_dir = tmp_dir + self.result_name
        self.wav_file = self.tmp_file_dir + '/audio.wav'
        self.json_file = root_dir + self.result_name + '.json'
        self.events = []
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        if not os.path.exists(self.tmp_file_dir):
            os.mkdir(self.tmp_file_dir)

    def run_only_frames(self, vid):
        ref_idx, fps = self.get_frame_info(vid)
        frame_times = self.get_idx_to_time(ref_idx, fps)
        print(frame_times)

    def run_only_sound(self, vid):
        sound_times = self.get_audio_times(vid)
        print(sound_times)

    def run(self, video_file):
        ref_idx, fps = self.get_frame_info(video_file)
        frame_times = self.get_idx_to_time(ref_idx, fps)
        sound_times = self.get_audio_times(video_file)
        count = min(len(frame_times), len(sound_times))

        delays = []
        event_list = []
        for i in range(count):
            delay = frame_times[i] - sound_times[i]
            event = {
                'frame event': frame_times[i],
                'audio event': sound_times[i],
                'delay event': delay
            }
            delays.append(delay)
            event_list.append(event)
            avg_delay = np.mean(delays)
        events = {
            'event list': event_list,
            'average delay': avg_delay
        }

        self.events.append(events)

    def get_frame_info(self, vid):
        cap = cv.VideoCapture(vid)
        fps = cap.get(cv.CAP_PROP_FPS)
        ref_dat = self.get_frame_ref_point(vid)
        ref_idx = self.get_peaks(ref_dat)
        return ref_idx, fps

    @staticmethod
    def get_idx_to_time(ref_idx, fps):
        frame_times = []
        for i in ref_idx:
            time = round(i/fps, 5)
            if time not in frame_times:
                frame_times.append(time)
        return frame_times

    @staticmethod
    def get_frame_ref_point(vid):
        cap = cv.VideoCapture(vid)
        frame_count = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
        dat = []
        i = 1
        while i <= frame_count:
            _, frame = cap.read()
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            width = len(gray_frame)
            assert width > 0, 'frame width is 0'
            height = len(gray_frame[0])
            assert height > 0, 'frame height is 0'
            ref_point = gray_frame[int(width / 2)][int(height / 2)]
            dat.append(ref_point)
            i += 1

        return dat

    @staticmethod
    def get_peaks(lis):
        z_list = stats.zscore(lis)
        z_mean = np.mean(z_list)
        upp_limit = 0.5 * (z_mean + max(z_list))

        index_list = []
        for i in range(len(z_list)):
            if z_list[i] > upp_limit:
                index_list.append(i)
        idx_list = [index_list[0]]
        for i in range(1, len(index_list)):
            if index_list[i] - index_list[i-1] > FRAME_INTERVAL:
                idx_list.append(index_list[i])
        return idx_list

    def get_audio_times(self, video_file):
        command = 'ffmpeg -i {} -ac 1 {}'.format(video_file, self.wav_file)
        subprocess.call(command, shell=True)

        t = wavfile.read(self.wav_file)
        amp = list(t[1][:int(len(t[1]))])
        z_list = stats.zscore(amp)
        z_list = list(z_list)
        z_mean = np.mean(z_list)
        n = 0.5 * (z_mean + max(z_list))

        index_list = []
        for i in range(len(z_list)):
            if z_list[i] > n:
                index_list.append(i)
        idx_list = []
        for i in range(1, int(len(index_list))):
            if index_list[i] - index_list[i - 1] > SAMPLE_GAP:
                idx_list.append(index_list[i])
        time_idx = [index_list[0]] + idx_list
        time_list_sound = [round(float(i / int(SAMPLE_RATE)), 5) for i in time_idx]
        return time_list_sound


def main(video_file, result_name):
    sync = AVSync(result_name)
    start = time.perf_counter()
    sync.run(video_file)
    end = time.perf_counter()
    time_taken = round(end - start, 3)
    print(f'finished running in {time_taken} seconds')
    with open(sync.json_file, 'w') as json_file:
        json.dump(sync.events, json_file)

@click.command()
@click.option('--file', type=str, help='video file path')
@click.option('--result', type=str, help='result_name')
def command(file, result):
    main(file, result)


if __name__ == '__main__':
    command()








