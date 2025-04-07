using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using UnityEngine;

public class GestureRequester : RunAbleThreadGesture {


    protected GestureClient gesClient;

    public bool active = true;


    public GestureRequester(GestureClient gesClient)
    {
        this.gesClient = gesClient;
    }


    /// <summary>
    ///     Requests a so far random position for the object from the server and receive message with position back. Should do it on button press.
    ///     
    /// </summary>
    protected override void Run()
    {

        ForceDotNet.Force(); // this line is needed to prevent unity freeze after one use, not sure why yet
        using (RequestSocket client = new RequestSocket())
        {
            client.Connect("tcp://localhost:5555");

            while (Running)
            {
                if (active)
                {
                    //Debug.Log("Requesting Gesture");
                    client.SendFrame("Gesture");
                }
                else
                {
                    Debug.Log("Requesting END");
                    client.SendFrame("END");
                    
                }

                
                // ReceiveFrameString() blocks the thread until you receive the string, but TryReceiveFrameString()
                // do not block the thread, you can try commenting one and see what the other does, try to reason why
                // unity freezes when you use ReceiveFrameString() and play and stop the scene without running the server
                //                string message = client.ReceiveFrameString();
                //                Debug.Log("Received: " + message);
                string gestureMessage = null;
                bool gotMessage = false;
                while (Running)
                {
                    gotMessage = client.TryReceiveFrameString(out gestureMessage); // this returns true if it's successful
                    if (gotMessage) break;
                }

                if (gotMessage && active)
                {
                    //Debug.Log("Received " + gestureMessage);
                    gesClient.gestureString = gestureMessage;
                    gesClient.newString = true;
                    
                }
                else if (gotMessage && !active)
                {
                    Debug.Log("Should END");
                    if (gestureMessage.Equals("END"))
                    {
                        Debug.Log("Stopped");
                        Running = false;
                    }
                }
            }
            


        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet
        
    }


}
