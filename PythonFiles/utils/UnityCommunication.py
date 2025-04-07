# Unity python communication
import zmq
import cv2


"""
Unity communication parameters
"""
# context = zmq.Context()
# socket = context.socket(zmq.REP)
# socket.bind("tcp://*:5555")
# unity_output = "-1"

UnityCommunication_ON = True

data = ""
triangles, squares, pentagons = "", "", ""

image = []


# def startCommunicationWithUnity():
#     while True:
#         ## unity communication
#         print("Started")
#         print("Data ", data)
#         if UnityCommunication_ON and data != "":
#             print("Waiting for unity")
#             message = socket.recv()
#             print("Received request: %s" % message)
#
#             stringMessage = message.decode("utf-8")
#             stringMessage = stringMessage.strip()
#             if stringMessage == "END":
#                 print("Should END")
#                 output_byte = str.encode("END")
#                 socket.send(b"%s" % output_byte)
#                 break
#
#             #  Send reply to client
#             #  In the real world usage, after you finish your work, send your output here
#             socket.send_json(data)
#
#
# def updateData(updatedData):
#     data = updatedData
#
#
# def updateDta(newTriangles, newSquares, newPentagons, newImage):
#     triangles = newTriangles
#     squares = newSquares
#     pentagons = newPentagons
#     image = newImage
#
#     data = {
#         'messageString': "Running",
#         'trianglesMessage': triangles,
#         'squaresMessage': squares,
#         'pentagonsMessage': pentagons,
#         'image': cv2.imencode('.jpg', image)[1].ravel().tolist()
#     }
