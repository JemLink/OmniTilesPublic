using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// This class is used as a container for the received data from python
/// </summary>
public class Data
{
    public string gestureString;
    public string contourString;
    public byte[] image;

    public static Data CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<Data>(jsonString);
    }

}
