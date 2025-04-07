using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using UnityEngine;

public class PositionRequester : RunAbleThreadPosition
{
    protected PositionClient posClient;


    public PositionRequester(PositionClient posClient)
    {
        this.posClient = posClient;
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

            Debug.Log("Requesting Position");
            client.SendFrame("Position");
            // ReceiveFrameString() blocks the thread until you receive the string, but TryReceiveFrameString()
            // do not block the thread, you can try commenting one and see what the other does, try to reason why
            // unity freezes when you use ReceiveFrameString() and play and stop the scene without running the server
            //                string message = client.ReceiveFrameString();
            //                Debug.Log("Received: " + message);
            string positionMessage = null;
            bool gotMessage = false;
            while (Running)
            {
                gotMessage = client.TryReceiveFrameString(out positionMessage); // this returns true if it's successful
                if (gotMessage) break;
            }

            if (gotMessage)
            {
                Debug.Log("Received " + positionMessage);
                posClient.positionString = positionMessage;
                posClient.newString = true;
            }

                

        }

        NetMQConfig.Cleanup(); // this line is needed to prevent unity freeze after one use, not sure why yet

       // this.Stop();
    }
    
    
}
