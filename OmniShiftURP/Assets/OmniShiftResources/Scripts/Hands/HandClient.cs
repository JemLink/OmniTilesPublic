using AsyncIO;
using NetMQ;
using NetMQ.Sockets;
using System;
using System.Collections.Concurrent;
using System.Threading;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.InputSystem;

public class HandClient : Client
{
    private readonly ConcurrentQueue<Action> runOnMainThread = new ConcurrentQueue<Action>();
    private HandReceiver receiver;


    [Header("Gesture Update")]
    public HandRepresentation handRep;


    [Header("Body Image")]
    private Texture2D tex;
    //public RawImage image;
    public Renderer rend;


    public void Awake()
    {
        if (rend)
        {
            tex = new Texture2D(2, 2, TextureFormat.RGB24, mipChain: false);
            //image.texture = tex;
            rend.material.SetTexture("_BaseMap", tex);
        }
    }

    public void Update()
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
        if (Input.GetKeyDown(KeyCode.Q))
        {
            receiver.active = false;
        }
    }

    private void OnDestroy()
    {
        
        receiver.Stop();
        //NetMQConfig.Cleanup();  // Must be here to work more than once
    }

    public override void StartCommunication()
    {
        ForceDotNet.Force();
        // - You might remove it, but if you have more than one socket
        //   in the following threads, leave it.
        receiver = new HandReceiver();
        receiver.Start((HandData d) => runOnMainThread.Enqueue(() =>
        {
            if (!(d).messageString.Equals("END"))
            {
                handRep.UpdateHandPose((d).messageString);
                if (rend)
                {
                    tex.LoadImage((d).image);
                }
                
            }


        }
        ));
    }

    public override void StopCommunication()
    {
        if (receiver != null)
        {
            receiver.Stop();
        }
    }
}
