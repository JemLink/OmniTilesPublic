using NetMQ;
using NetMQ.Sockets;
using System;
using System.Collections.Concurrent;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;

public class DrawReceiver
{
    private readonly Thread receiveThread;
    private bool running;

    public bool active = true;

    public DrawReceiver()
    {
        receiveThread = new Thread((object callback) =>
        {
            using (var socket = new RequestSocket())
            {
                socket.Connect("tcp://localhost:5555");

                while (running)
                {


                    if (active)
                    {
                        socket.SendFrame("DRAWING");
                    }
                    else
                    {
                        Debug.Log("Requesting END");
                        socket.SendFrame("END");
                    }

                    string message = null;
                    bool gotMessage = false;

                    while (running)
                    {
                        gotMessage = socket.TryReceiveFrameString(out message);
                        if (gotMessage) break;
                    }
                    //string message = socket.ReceiveFrameString();

                    if (gotMessage && active)
                    {
                        DrawData data = JsonUtility.FromJson<DrawData>(message);
                        ((Action<DrawData>)callback)(data);
                    }
                    else if (gotMessage && !active)
                    {
                        Debug.Log("Should END");
                        if (message.Equals("END"))
                        {
                            Debug.Log("Stopped");
                            running = false;
                        }
                    }


                }
            }

            NetMQConfig.Cleanup();

        });
    }


    public void Start(Action<DrawData> callback)
    {
        running = true;
        receiveThread.Start(callback);
    }

    public void Stop()
    {
        active = false;
        running = false;
        receiveThread.Join();
    }

}