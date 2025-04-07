using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using System;
using System.Collections.Concurrent;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;

public class TilesClient : Client
{
    private readonly ConcurrentQueue<Action> runOnMainThread = new ConcurrentQueue<Action>();
    private TilesReceiver receiver;


    [Header("Update Actions")]
    public TilesDataHandler dataHandler;



    public override void StartCommunication()
    {

        ForceDotNet.Force();
        // - You might remove it, but if you have more than one socket
        //   in the following threads, leave it.
        receiver = new TilesReceiver();
        receiver.Start((TilesData d) => runOnMainThread.Enqueue(() =>
        {
            if (!d.messageString.Equals("END"))
            {
                dataHandler.SetData(d);
            }


        }
        ));
    }
    

    public void FixedUpdate()
    {
        if (!runOnMainThread.IsEmpty)
        {
            Action action;
            while (runOnMainThread.TryDequeue(out action))
            {
                action.Invoke();
            }
        }

        // use this to stop client server connection
        if (Input.GetKeyDown(KeyCode.Q) && receiver != null)
        {
            receiver.active = false;
        }
    }


    public override void StopCommunication()
    {
        if (receiver != null)
        {
            receiver.Stop();
        }
    }


    private void OnDestroy()
    {
        StopCommunication();
        
    }
}
