using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TilesData
{
    public string messageString;
    public string trianglesMessage;
    public string squaresMessage;
    public string pentagonsMessage;
    
    public byte[] image;

    public static Data CreateFromJSON(string jsonString)
    {
        return JsonUtility.FromJson<Data>(jsonString);
    }
    
}
