from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))
      
!ls -al

# use path to load into numpy array
#selected_image = '20170423_131504.jpg' 
#image_np = load_image_into_numpy_array(selected_image)

from PIL import Image
im = Image.open(path+item)
imResize = im.resize((254,254), Image.ANTIALIAS)

#im = Image.open(path+item)
#f, e = os.path.splitext(path+item)
#imResize = im.resize((254,254), Image.ANTIALIAS)
#imResize.save(f+'.png', 'png', quality=80)
