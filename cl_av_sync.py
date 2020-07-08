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

from Common import *


class AVSync(object):
    def __init__(self, result_name):
        super(AVSync, self).__init__()
        cur_time = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.result_name = cur_time + '_' + result_name
        self.tmp_file_dir = tmp_dir + self.result_name
        self.wav_file = self.tmp_file_dir + '/audio.wav'
        self.txt_file = root_dir + self.result_name + '.txt'
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        if not os.path.exists(self.tmp_file_dir):
            os.mkdir(self.tmp_file_dir)

    def run(self, video_file):
        frame_times = self.get_frame_info(video_file)
        sound_times = self.get_audio_times(video_file)
        count = min(len(frame_times), len(sound_times))

        delays = []
        for i in range(count):
            delay = frame_times[i] - sound_times[i]
            delays.append(delay)

        avg_delay = np.mean(delays)
        with open(self.txt_file, 'w') as f:
            f.write(f'delay list: {delays}\n')
            f.write(f'avg delay: {avg_delay}')

    def get_frame_info(self, vid):
        ts = self.get_video_frame_ts(video_file=vid)
        ref_dat = self.get_frame_ref_point(vid)
        assert len(ts) == len(ref_dat), f'timestamp length != frame data length: {len(ts)}, {len(ref_dat)}'
        ref_idx = self.get_peaks(ref_dat)

        frame_times = []
        for i in ref_idx:
            time = ts[i]
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
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            width = len(gray)
            assert width > 0, f'frame data missing, frame width = {width}'
            height = len(gray[0])
            assert height > 0, f'frame data missing, frame height = {height}'
            ref_point = gray[int(width/2)][int(height/2)]
            dat.append(ref_point)
            i += 1
        return dat

    def get_video_frame_ts(self, video_file):
        tmp_file = tmp_dir + self.result_name + '/tmp_frame_ts.txt'
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        command = f"ffprobe -i {video_file} -show_frames > {tmp_file}"
        p = subprocess.Popen(command, shell=True)
        p.wait()

        ret = []
        data = get_file_data(tmp_file)
        print(f'tmp file is {tmp_file}')
        lines = data.strip().split()
        for line in lines:
            if line.startswith('pkt_pts_time'):
                ret.append(safe_cast(line.split('=')[1], float, 0.0))
        return ret

    @staticmethod
    def get_peaks(lis):
        z_list = stats.zscore(lis)
        z_mean = np.mean(z_list)
        upp_limit = 0.5 * (z_mean + max(z_list))

        index_list = []
        for i in range(len(z_list)):
            if z_list[i] > upp_limit:
                index_list.append(i)
        idx_list = []
        for i in range(1, len(index_list)):
            if index_list[i] - index_list[i-1] > FRAME_INTERVAL:
                idx_list.append(index_list[i])
        return idx_list

    def get_audio_times(self, video_file):
        command = 'ffmpeg -i %s -ac 1 %s'.format(video_file, self.wav_file)
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
        time_list_sound = [float(i / int(SAMPLE_RATE)) for i in time_idx]
        return time_list_sound


def main(video_file, result_name):
    sync = AVSync(result_name)
    sync.run(video_file)

@click.command()
@click.option('--file', type=str, help='video file path')
@click.option('--result', type=str, help='result_name')
def command(file, result):
    main(file, result)


if __name__ == '__main__':
    command()








