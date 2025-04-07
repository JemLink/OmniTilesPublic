using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ContourData : Data
{
    public string gestureString;
    public string contourString;
    public byte[] image;

    new public static Data CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<Data>(jsonString);
    }
}
