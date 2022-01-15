from facenet_pytorch import MTCNN,InceptionResnetV1
import torch,cv2,time,os,pickle
import numpy as np
rootDir = "C://Users//pc//PycharmProjects//ICS_PROJECT//"
mtcnn = MTCNN(image_size=240, margin=0, keep_all=True, min_face_size=40)
#resnet = InceptionResnetV1(pretrained='vggface2').eval()

#IMPORTING THE MAIN NEURAL NETWORK BEHIND THE FACIAL RECOGNITION
resnet = pickle.load(open(rootDir+"resnetModel.p","rb"))

def getFaceEmbedding(face):
    emb = resnet(face.unsqueeze(0))
    return emb.detach()
    print("?")