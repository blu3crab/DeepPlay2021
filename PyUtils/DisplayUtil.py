###############################################################################
__author__ = "M.A.Tucker"
__license__ = "Apache License 2.0"
__version__ = "0.0.1"
#
# import
#   from PyUtils.DisplayUtil import displayGrayImageAtIndex
# invoke
#   displayGrayImageAtIndex(x_train, 1)
###############################################################################

import numpy as np
import matplotlib.pyplot as plt

###############################################################################
# purpose
#   display MNIST like image from dataset at index
# import
#   from PyUtils.DisplayUtil import displayGrayImageAtIndex
# invoke
#   displayGrayImageAtIndex(x_train, 1)
#
import numpy as np
import matplotlib.pyplot as plt
def displayGrayImageAtIndex(imageData, imageIndex):
    image = imageData[imageIndex]
    image = np.array(image, dtype='float')
    pixels = image.reshape((28, 28))
    plt.imshow(pixels, cmap='gray')
    plt.show()

def displayColorImageAtIndex(imageData, imageIndex):
    plt.figure()
    plt.imshow(imageData[imageIndex])
    plt.colorbar()
    plt.grid(True)
    plt.show()

def displayImageLabelRange(imageData, imageLabels, classNames, startIndex, endIndex):
    plt.figure(figsize=(10, 10))
    for i in range(startIndex, endIndex):
        plt.subplot(5, 5, i + 1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.imshow(imageData[i], cmap=plt.cm.binary)
        plt.xlabel(classNames[imageLabels[i]])
    plt.show()

# plot training & validation loss
def
    acc = history_dict['accuracy']
    val_acc = history_dict['val_accuracy']
    loss = history_dict['loss']
    val_loss = history_dict['val_loss']
    print("loss -> ", loss)
    print("val_loss -> ", val_loss)

    epochs = range(1, len(acc) + 1)

    # "bo" is for "blue dot"
    plt.plot(epochs, loss, 'bo', label='Training loss')
    # b is for "solid blue line"
    plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training and validation loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.show()

    # plot training & validation accuracy
    epochs = range(1, len(acc) + 1)

    plt.clf()  # clear figure

    plt.plot(epochs, acc, 'bo', label='Training acc')
    plt.plot(epochs, val_acc, 'b', label='Validation acc')
    plt.title('Training and validation accuracy')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend(loc='lower right')

    plt.show()