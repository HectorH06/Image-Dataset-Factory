import os
import pandas as pd
from tensorflow.keras.preprocessing.image import load_img, img_to_array, ImageDataGenerator
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, Dropout, BatchNormalization
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import LabelEncoder

#region Read data
train_df = pd.read_csv('img/data/train_dataset.csv')
test_df = pd.read_csv('img/data/test_dataset.csv')

base_dir = os.getcwd()

folder_Train = os.path.join(base_dir, 'img', 'train')
folder_Test = os.path.join(base_dir, 'img', 'test')

img_size = (227, 227)  # Cambiamos el tamaño de imagen a 227x227
# endregion

#region Data Augmentation
datagen = ImageDataGenerator(
    rotation_range=15,
    width_shift_range=0.1,
    height_shift_range=0.1,
    brightness_range=[0.8, 1.2],
    horizontal_flip=True
)
#endregion

#region Load Dataframe
def load_images_from_df(df, folder):
    images = []
    labels = []
    for index, row in df.iterrows():
        class_name = row['target']
        img_path = os.path.join(folder, class_name, row['filename'])
        try:
            img = load_img(img_path, target_size=img_size)
            img_array = img_to_array(img)
            images.append(img_array)
            labels.append(class_name)
        except FileNotFoundError:
            print(f"El archivo no fue encontrado: {img_path}")
    return np.array(images), labels
#endregion

#region Load imgs, codify labels and normalize imgs
X_train, y_train = load_images_from_df(train_df, folder_Train)
X_test, y_test = load_images_from_df(test_df, folder_Test)

label_encoder = LabelEncoder()

y_train_encoded = label_encoder.fit_transform(y_train)
y_test_encoded = label_encoder.transform(y_test)

y_train_one_hot = to_categorical(y_train_encoded)
y_test_one_hot = to_categorical(y_test_encoded)

X_train = X_train.astype('float32') / 255.0
X_test = X_test.astype('float32') / 255.0
#endregion

#region TRUE ALEXNET
def alex(input_shape, num_classes):
    model = Sequential()

    # First layer
    model.add(Conv2D(96, (11, 11), strides=4, activation='relu', input_shape=input_shape))
    model.add(MaxPooling2D(pool_size=(3, 3), strides=2))
    model.add(BatchNormalization())

    # Second layer
    model.add(Conv2D(256, (5, 5), padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(3, 3), strides=2))
    model.add(BatchNormalization())

    # Third, fourth, fifth (convolutional)
    model.add(Conv2D(384, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(384, (3, 3), padding='same', activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(256, (3, 3), padding='same', activation='relu'))
    model.add(MaxPooling2D(pool_size=(3, 3), strides=2))
    model.add(BatchNormalization())

    # Connected ones
    model.add(Flatten())
    model.add(Dense(4096, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(4096, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))

    return model
#endregion

#region Params, model and else
input_shape = (img_size[0], img_size[1], 3)
num_classes = len(label_encoder.classes_)

model = alex(input_shape, num_classes)
model.compile(optimizer=Adam(learning_rate=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

model.summary()

# Training the model with augmented data
batch_size = 16  # Reducimos el tamaño de batch
epochs = 30  # Incrementamos las épocas

history = model.fit(
    datagen.flow(X_train, y_train_one_hot, batch_size=batch_size),
    epochs=epochs,
    validation_data=(X_test, y_test_one_hot)
)

test_loss, test_acc = model.evaluate(X_test, y_test_one_hot)
print(f"Precisión en el conjunto de prueba: {test_acc}")
#endregion