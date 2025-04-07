using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GestureClient : MonoBehaviour
{

    private GestureRequester gestureRequester;
    public string gestureString = "-1";
    public bool newString = false;


    public HandRepresentation handRep;



    //public GameObject testObject;

    // Use this for initialization
    void Start()
    {
        gestureRequester = new GestureRequester(this);
        gestureRequester.Start();

    }

    void Update()
    {

        // use this to stop client server connection
        if (Input.GetKeyDown(KeyCode.Q))
        {
            gestureRequester.active = false;
        }
        

        if (newString)
        {
            //Debug.Log("Gesture: " + gestureString);
            newString = false;

            handRep.UpdateHandPose(gestureString);
            //testObject.GetComponent<Renderer>().material.color = ChangeColorOnIndex(gestureString);
        }
    }



    private void OnDestroy()
    {
        gestureRequester.Stop();
    }







    private Vector3 ConvertPositionMessageToPosition(string message)
    {
        float[] floatData = Array.ConvertAll(message.Split(','), float.Parse);

        Vector3 returnVec = new Vector3(floatData[0], floatData[1], floatData[2]);

        return returnVec;
    }

    //private Vector3[] GetHandLandmarks(string message)
    //{
    //    string[] stringData = message.Split(';');
    //    float[] floatData = Array.ConvertAll(message.Split(';'), float.Parse);

    //    Vector3 returnVec = new Vector3(floatData[0], floatData[1], floatData[2]);

    //    return returnVec;
    //}

    private Color ChangeColorOnIndex(string index_string)
    {
        int id = int.Parse(index_string);
        

        Color returnCol = Color.white;

        switch (id)
        {
            case -1:
                // this is the fallback when no gesture is detected
                returnCol = Color.white;
                break;
            case 0:
                returnCol = Color.red;
                break;
            case 1:
                returnCol = Color.blue;
                break;
            case 2:
                returnCol = Color.green;
                break;
            default:
                Debug.LogWarning("No color found in switch case");
                break;
        }

        return returnCol;
    }
}
