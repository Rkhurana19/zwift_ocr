from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import pytesseract
import os
import re

class Batch_Image_Processing:
	def __init__(self, input_path):
		self.input_path = input_path
		os.chdir(input_path)

	def crop_images(self, left, upper, right, lower, crop_label, output_path):
		for image_name in os.listdir():
			if (image_name != ".DS_Store"):
				img = Image.open(image_name)

				width, height = img.size

				# dimensions for cropped rectangle; parameters represent directionals
				crop_specs = (left, upper, width - right, height - lower)

				crop_img = img.crop(crop_specs)
				resizedImage = crop_img.resize((90, 44)) # consistent size
				resizedImage.save(output_path + "/" + crop_label + " " + image_name, 
					dpi = (300, 300))

	def sharpen_images(self, output_path):
		for image_name in os.listdir():
			if (image_name != ".DS_Store"):
				img = Image.open(image_name)
				enhancer = ImageEnhance.Sharpness(img)

				# factor of 4 enhances the image
				enhancer.enhance(4).save((output_path + "/" + "sharpened " 
					+ image_name), dpi = (300, 300)) 

	def binarize_images(self, output_path):
		# binarization scheme adopted from "https://note.nkmk.me/en/python-numpy-opencv-image-binarization/"
		for image_name in os.listdir():
			if (image_name != ".DS_Store"):
				img = np.array(Image.open(image_name).convert("L")) # convert to grayscale
				im_bin = (img > 128) * 255 # simple thresholding to binarize image

				new_img = Image.fromarray(np.uint8(im_bin))

				# slight blur to remove pixelation  
				img_blur = new_img.filter(ImageFilter.GaussianBlur(0.50))
				img_blur.save(output_path + "/" + "Binary " + image_name, 
					dpi = (300, 300))

	def apply_tesseract(self, label):
		tesseract_results = ""

		# sort files numerically 
		files = np.array([file for file in os.listdir() if file != ".DS_Store"])
		numbers = np.array([re.findall("\d+", element) for element in files 
			if element != ".DS_Store"]).reshape(len(files), )

		zipped_files = set(zip(files, map(int, numbers)))
		sorted_files = sorted(zipped_files, key = lambda item : item[1])

		# run tesseract
		for image_name, capture_number in sorted_files:
			img = Image.open(image_name)
			ocr_text = pytesseract.image_to_string(image_name, 
				config = "--psm 7 outputbase digits")

			# appropriate modification for HR readings (ignore heart symbol output)
			if (ocr_text.isdigit() and label == "HR"):
				while (int(ocr_text) > 300):
					ocr_text = ocr_text[:-1]

			# appropriate modification for Power readings (ignore "w" output)
			if ("." in ocr_text and label == "Power"):
				ocr_text = ocr_text.replace(".", "")

			print(image_name + " - " + ocr_text) # see results live

			tesseract_results += image_name + " - " + ocr_text + "\n"

		# write to output
		with open("tesseract_results.txt", "w") as f:
			f.write("{}".format(tesseract_results))

def count_blanks(tesseract_txt):
	with open(tesseract_txt, "r") as f:
		lines = f.readlines()
		tesseract_results = [line.split(" ")[-1] for line in lines]
		
		correct = 0
		total = 0

		# count number of blanks and use it as a metric for determining efficiency
		for result in tesseract_results:
			total += 1
			if result.strip().isdigit():
				correct += 1

		return (correct / total) * 100
		