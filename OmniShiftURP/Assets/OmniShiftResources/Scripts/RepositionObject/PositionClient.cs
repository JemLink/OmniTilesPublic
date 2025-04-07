using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PositionClient : MonoBehaviour {

    private PositionRequester positionRequester;
    public string positionString =  "";
    public bool newString = false;



    public Vector3 testVector;
    public GameObject testObject;
    
	// Use this for initialization
	void Start () {
        
        
    }

    void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space))
        {
            if(positionRequester != null)
            {
                positionRequester.Stop();
            }

            positionRequester = new PositionRequester(this);
            positionRequester.Start();

            

        }

        if (newString)
        {
            testVector = ConvertPositionMessageToPosition(positionString);
            newString = false;

            testObject.transform.position = testVector * 10.0f;
        }
    }


    private void OnDestroy()
    {
        positionRequester.Stop();
    }


    private Vector3 ConvertPositionMessageToPosition(string message)
    {
        float[] floatData = Array.ConvertAll(message.Split(','), float.Parse);

        Vector3 returnVec = new Vector3(floatData[0], floatData[1], floatData[2]);

        return returnVec;
    }
}
