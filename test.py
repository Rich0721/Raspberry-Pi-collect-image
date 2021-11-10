for roi in self.condition_roi:
                
    template = self.condition_image[roi[1]:roi[3], roi[0]:roi[2]]
    if self.settings['SSIM']:
        score = self.ssim(frame[roi[1]:roi[3], roi[0]:roi[2]], template, multichannel=True)
        if score >= THRESHOLD:
            storages.append("True")
