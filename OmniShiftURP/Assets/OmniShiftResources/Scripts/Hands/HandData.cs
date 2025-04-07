using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HandData
{
    public string messageString;
    public byte[] image;

    public static Data CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<Data>(jsonString);
    }
}