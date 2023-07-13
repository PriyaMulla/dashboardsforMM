import TimeTagger as TT
from TimeTagger import Flim, TimeTagStream, createTimeTaggerVirtual, EventGenerator, Countrate,ConstantFractionDiscriminator, DelayedChannel
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import sys

filename = sys.argv[1]

#swabian configs
laser = 1
click = laser
frame = 3 
frame_n = -3
line = 2
line_n = -2
photon = -4
n_bins = 256
binwidth = 49 # 12.5ns/256
n_pixel = 256
laser_frequency = 80e6  # 1/12.5ns
pixel_rate = 200e3
pixel_time = 1 / pixel_rate
integr_time = 3e9 # Integration time of 3 ms in picoseconds


time_tag_virt=TT.createTimeTaggerVirtual()

# EventGenerator(tagger, trigger_channel, pattern, trigger_divider, stop_channel)
pixel_start_channel = EventGenerator(time_tag_virt, line, pixel_pattern_start)
pixel_start = pixel_start_channel.getChannel()

pixel_end_channel= EventGenerator(time_tag_virt, line, pixel_pattern_end)
pixel_end = pixel_end_channel.getChannel()

#ConstantFractionDiscriminator(tagger, channels, search_window)
photon_cfd_chan = ConstantFractionDiscriminator(time_tag_virt, (photon,), 10*1000)
photon_cfd = photon_cfd_chan.getChannels()[0]

#DelayedChannel(tagger, input_channel, delay)
delayed_sync_chan = DelayedChannel(time_tag_virt, laser, 11.5e3)
delayed_sync = delayed_sync_chan.getChannel()

#flim set up
flim = Flim(time_tag_virt, start_channel=delayed_sync, click_channel=photon_cfd, pixel_begin_channel=pixel_start, n_pixels=n_pixel*n_pixel,
             n_bins=n_bins, binwidth=binwidth, pixel_end_channel=pixel_end, frame_begin_channel=frame)

#replay
time_tag_virt.setReplaySpeed(-1)
replay = time_tag_virt.replay(filename)
time_tag_virt.waitForCompletion()

#shape image 256x256
flim_frames = flim.getSummedFrames()
flim_2d = flim_frames.reshape(256,256,256)
flim_mean = flim_2d.mean(2)

#show image
plt.figure(figsize=[7,7])
plt.imshow(flim_mean,vmax=.035)
plt.colorbar()
plt.figure()
#plot photons
plt.plot(flim_2d.sum((0,1)))
plt.show()

