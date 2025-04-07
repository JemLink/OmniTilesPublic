using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DrawData
{
    public string messageString;
    public string centerMessage;

    public byte[] image;

    public static Data CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<Data>(jsonString);
    }
}
