filenames = ['pytorch_model-00001-of-00002.bin', 'pytorch_model-00002-of-00002.bin']
output_filename = 'merged_pytorch_model.bin'

with open(output_filename, 'wb') as output_file:
    for filename in filenames:
        with open(filename, 'rb') as input_file:
            output_file.write(input_file.read())
