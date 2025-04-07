using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using System;
using System.Collections.Concurrent;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;

public abstract class Client : MonoBehaviour
{
    public abstract void StartCommunication();

    public abstract void StopCommunication();

    //this class should just be used as an interface

    //private readonly ConcurrentQueue<Action> runOnMainThread = new ConcurrentQueue<Action>();
    //private Receiver receiver;


    //[Header("Update Actions")]
    //public DataHandler dataHandler;



    //public void Start()
    //{

    //    ForceDotNet.Force();
    //    // - You might remove it, but if you have more than one socket
    //    //   in the following threads, leave it.
    //    receiver = new Receiver();
    //    receiver.Start((Data d) => runOnMainThread.Enqueue(() =>
    //    {
    //        if (!d.gestureString.Equals("END"))
    //        {
    //            dataHandler.SetData(d);
    //        }


    //    }
    //    ));
    //}

    //public void Update()
    //{
    //    if (!runOnMainThread.IsEmpty)
    //    {
    //        Action action;
    //        while (runOnMainThread.TryDequeue(out action))
    //        {
    //            action.Invoke();
    //        }
    //    }

    //    // use this to stop client server connection
    //    if (Input.GetKeyDown(KeyCode.Q))
    //    {
    //        receiver.active = false;
    //    }
    //}

    //private void OnDestroy()
    //{

    //    receiver.Stop();
    //    //NetMQConfig.Cleanup
    //}
}
