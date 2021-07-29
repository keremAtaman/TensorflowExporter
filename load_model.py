from tensorflow import keras
model = keras.models.load_model('Customer1019DataModel.h5')
i=0
for layer in model.layers:
    print("--------Layer " + str(i) + "--------")
    print("name: " + layer.name)
    print("input shape: " + str(layer.input_shape))
    print("output shape: " + str(layer.output_shape))
    i+=1

print('done')