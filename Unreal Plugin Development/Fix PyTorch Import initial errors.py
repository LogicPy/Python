import os

# Specify the directory you want to start from
rootDir = 'E:/ai_integration2/MyProject8/Plugins/GPT2_Conv_AI_Plugin_UE/Source/GPT2_Conv_AI_Plugin_UE/ThirdParty/pytorch-main (2)'

for dirName, subdirList, fileList in os.walk(rootDir):
    for fname in fileList:
        if fname.endswith('.cpp'):
            include = '#include "{}"'.format(fname.replace('.cpp', '.h'))
            
            with open(os.path.join(dirName, fname), 'r', encoding='utf-8') as f:
                content = f.read()
            with open(os.path.join(dirName, fname), 'w', encoding='utf-8') as f:
                f.write(include + '\n' + content)

print("Done!")
