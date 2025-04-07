using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Hand : MonoBehaviour {

    /*
     * Mediapipes indexing is as follows:
     * 0: wrist                     13: ring_MCP
     * 1: thumb_CMC                 14: ring_PIP
     * 2: thumb_MCP                 15: ring_DIP
     * 3: thumb_IP                  16: ring_TIP
     * 4: thumb_TIP                 17: pinky_MCP
     * 5: index_MCP                 18: pinky_PIP
     * 6: index_PIP                 19: pinky_DIP
     * 7: index_DIP                 20: pinky_TIP
     * 8: index_TIP
     * 9: middle_MCP
     * 10: middle_PIP
     * 11: middle_DIP
     * 12: middle_TIP
     * 
     * */



   // public GameObject jointsRepresenatation;
    public GameObject[] jointsRep;
    public Vector3[] joints;
    public int gestureID = -1;

    public BoxCollider handCollider;


    // Add more gestures in here when the model is trained for them
    // NOTE: They should be in the same order as in the training model
    public enum Gesture { Open, Closed, Pointer }
    public Gesture gesture;

    public bool gestureChanged = false;

    private Gesture lastGesture;

    public Hand()
    {
        joints = new Vector3[21];

        for(int i = 0; i < joints.Length; i++)
        {
            joints[i] = Vector3.zero;
        }


    }






    // Use this for initialization
    void Start () {
        if(handCollider == null)
        {
            handCollider = GetComponent<BoxCollider>();
            UpdateCollider();
        }
	}
	
	// Update is called once per frame
	void Update () {
        ChangeColorOnGesture();
        UpdateCollider();
    }
















    public void UpdateHandPos(string message)
    {
        // decode message and receive vector3 and gesture
        string jointString = GetSubstringWithoutGesture(message);

        // set joints position
        joints = GetVectorArrayFromString(jointString);

        // for representation
        UpdateJointsRep();
    }


    /// <summary>
    /// Updates the size and center of the collider that encapsulates the whole hand so that it can be used for 
    /// collision detection
    /// </summary>
    private void UpdateCollider()
    {

        Bounds bounds = new Bounds(joints[0], Vector3.zero);//(joints[0], jointsRep[0].transform.localScale);

        for(int i = 0; i < joints.Length; i++)
        {
            bounds.Encapsulate(joints[i]);
        }
        
        handCollider.size = bounds.size;
        handCollider.center = bounds.center;
        
    }



    /// <summary>
    /// This functions should receive a string starting with the an int indicating the gesture (-1 is no gesture was found)
    /// It should have the form:
    /// int:[x,y,z];[...]
    /// NOTE: this ':' should be the only one in the message!
    /// It will then separate the int and determine the gesture from it and return the string containing the joints positions
    /// </summary>
    /// <param name="message"></param>
    /// <returns></returns>
    private string GetSubstringWithoutGesture(string message)
    {
        string[] subMessages = message.Split(':');

        if (subMessages.Length > 2)
        {
            Debug.LogError("Message had more than one ':', the second submessage will be returned");
        }
        UpdateGesture(subMessages[0]);

        return subMessages[1];

    }

    /// <summary>
    /// This Function should receive a message in the form of
    /// [x,y,z];[x,y,z];[...]
    /// </summary>
    /// <param name="message"></param>
    /// <returns></returns>
    private Vector3[] GetVectorArrayFromString(string message)
    {
        string[] jointStrings = message.Split(';');

        Vector3[] jointVectors = new Vector3[jointStrings.Length];

        for (int i = 0; i < jointStrings.Length; i++)
        {
            jointVectors[i] = GetVectorFromString(jointStrings[i]);
        }

        return jointVectors;
    }



    /// <summary>
    /// This function should receive string parts in the form of [x,y,z]
    /// </summary>
    /// <param name="str"></param>
    /// <returns></returns>
    private Vector3 GetVectorFromString(string str)
    {
        Vector3 returnVec = Vector3.zero;

        if (str.StartsWith("[") && str.EndsWith("]"))
        {
            str = str.Substring(1, str.Length - 2); // this erazes the the brackets around the vector values
        }
        else
        {
            Debug.LogError("No suitable format found. Zero Vector will be returned");
            return Vector3.zero;
        }

        float[] values = Array.ConvertAll(str.Split(','), float.Parse);


        // the y value needs to be negative since unity and python (openCV) have different coordinate systems

        // values from python need to be converted to unity system
        // in python: (0,0) is left top corner
        // in unity: (0,0) is center of screen

        return ConvertPythonToUnityCoordinates(values[0], values[1], values[2]);

    }



    private void UpdateGesture(string strID)
    {
        

        gestureID = int.Parse(strID);
        gesture = (Gesture)gestureID;

        if(gesture != lastGesture)
        {
            gestureChanged = true;
        }

        SetGestureToValid();

        lastGesture = gesture;
    }


    

    private void UpdateJointsRep()
    {
        for (int i = 0; i < joints.Length; i++)
        {
            jointsRep[i].transform.localPosition = joints[i];
        }
    }


    public void DestroyHand()
    {
        for(int i = 0; i < jointsRep.Length; i++)
        {
            Destroy(jointsRep[i]);
        }
        
    }




    #region conversion

    /// <summary>
    /// This function takes a normalized Vector in python coordinates ((0,0) is left top corner)
    /// and converts it to normalized unity coordinates ((0,0) is center of screen)
    /// </summary>
    /// <param name="pythonVector"></param>
    /// <returns></returns>
    public Vector3 ConvertPythonToUnityCoordinates(Vector3 pythonVector)
    {
        float x = (pythonVector.x * 2.0f) - 1.0f;
        float y = (pythonVector.x * 2.0f) - 1.0f;
        float z = pythonVector.z;//(pythonVector.x * 2.0f) - 1.0f;

        return new Vector3(-x, y, z);
    }

    /// <summary>
    /// This function takes a normalized Vector in python coordinates ((0,0) is left top corner)
    /// and converts it to normalized unity coordinates ((0,0) is center of screen). 
    /// Also it mirrors the x axis since unity cooredinates are different coordinate system
    /// </summary>
    /// <param name="pythonVector"></param>
    /// <returns></returns>
    public Vector3 ConvertPythonToUnityCoordinates(float px, float py, float pz)
    {
        float x = (px * 2.0f) - 1.0f;
        float y = (py * 2.0f) - 1.0f;
        float z = pz;//(pythonVector.x * 2.0f) - 1.0f;

        return new Vector3(-x, y, z);
    }


    #endregion



    #region hand coloring and joint init


    private void OnValidate()
    {
        if (jointsRep.Length != 21)
        {
            jointsRep = new GameObject[21];
        }



        Joint[] joints = GetComponentsInChildren<Joint>();

        if (joints.Length == 21)
        {
            for (int i = 0; i < jointsRep.Length; i++)
            {
                jointsRep[i] = joints[i].gameObject;
            }
        }


    }


    private void SetGestureToValid()
    {
        switch (gestureID)
        {
            case 0:
                break;
            case 1:
                break;
            case 2:
                break;
            case -1:
                gestureID = (int)lastGesture;
                gesture = lastGesture;
                break;
            default:
                gestureID = (int)lastGesture;
                gesture = lastGesture;
                break;
        }
    }



    private void ChangeColorOnGesture()
    {
        switch (gestureID)
        {
            case 0:
                ChangeColorOfChildren(Color.red);
                break;
            case 1:
                ChangeColorOfChildren(Color.blue);
                break;
            case 2:
                ChangeColorOfChildren(Color.green);
                break;
            case -1:
                //ChangeColorOfChildren(Color.white);
                break;
            default:
                //ChangeColorOfChildren(Color.white);
                // no hand detected: change to white
                break;
        }
    }

    private void ChangeColorOfChildren(Color col)
    {
        Joint[] joints = GetComponentsInChildren<Joint>();

        for (int i = 0; i < joints.Length; i++)
        {
            joints[i].gameObject.GetComponent<Renderer>().material.color = col;
        }

    }

    #endregion




}
