import PIL
import collections
import matplotlib
import matplotlib.pyplot as plt
import torch
from torchvision import transforms
from google.colab import files



_IMAGE_UNLOADER = transforms.Compose([
  transforms.Lambda(lambda x: x.cpu().clone().squeeze(0)),
  transforms.ToPILImage()
])

def upload_files():
  """
  Creates a widget to upload files from your local machine to Colab.

  The files are saved in '/tmp/<file_name>'.
  """
  uploaded = files.upload()
  for name, data in uploaded.items():
    with open(f'/tmp/{name}', 'wb') as f:
      f.write(data)
    break
  return name


def load_image(path, size=None, remove_alpha_channel=True,  cap=2048):
  """Loads an image from the given path as a torch.Tensor.

  Args:
    path: The path to the image to load.
    size: Either None, an integer, or a pair of integers. If not None, the 
      image is resized to the given size before being returned.
    remove_alpha_channel: If True, removes the alpha channel from the image.
    cap = The upper limit on the size of loaded image. The image will be downscaled 
      to this size if it is larger than this.
  Returns:
    The loaded image as a torch.Tensor.
  """

  image = PIL.Image.open(path)
  image = transforms.ToTensor()(image)

  if size is not None:
    size = size if isinstance(size, collections.Sequence) else (size, size)
    assert len(size) == 2, "'size' must either be a scalar or contain 2 items"
    image = transforms.Resize(size)(image)
  else:
    if image.size()[1] > 2048 or image.size()[2] > 2048:
      if image.size()[1] >= image.size()[2]:
        factor = image.size()[1] / 2048
        other = int(image.size()[2] / factor)
        size = (2048, other)
      else:
        factor = image.size()[2] / 2048
        other = int(image.size()[1] / factor)
        size = (other, 2048)
      image = transforms.Resize(size)(image)

  if remove_alpha_channel:
      image = image[:3, :, :]
  image = image.to(torch.float)

  return image
  

def save_image(tensor, path, size=None):
  """Saves an image to the given path.

  Args:
    tensor: The tensor to render as an image. 
    path: The path to save the image at.
    size: Either None, an integer, or a pair of integers. If not None, the 
      image is resized to the given size before being returned.
  """

  transform = []
  if size is not None:
    size = size if isinstance(size, collections.Sequence) else (size, size)
    assert len(size) == 2, "'size' must either be a scalar or contain 2 items"
    transform.append(transforms.Resize(size))
  transform.append(transforms.Lambda(lambda x: x.cpu().clone().squeeze(0)))
  transform.append(transforms.ToPILImage())
  image_saver = transforms.Compose(transform)

  image = image_saver(tensor)
  image.save(path)

def imshow(tensor, title=None, figsize=None):
  """Renders the given tensor as an image using Matplotlib.

  Args:
    tensor: The tensor to render as an image.
    title: The title for the rendered image. Passed to Matplotlib.
    figsize: The size (in inches) for the image. Passed to Matplotlib.
  """
  image = _IMAGE_UNLOADER(tensor)

  plt.figure(figsize=figsize)
  plt.title(title)
  plt.axis('off')
  plt.imshow(image)
  plt.show()