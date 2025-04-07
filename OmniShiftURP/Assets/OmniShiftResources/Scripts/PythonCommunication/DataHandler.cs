using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DataHandler : MonoBehaviour
{
    private Data data;
    public string message;

    private string gestureString;
    private string contourString;

    [Header("Image handling")]
    private Texture2D tex;
    public Renderer rend;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void SetMessage(string message)
    {
        this.message = message;
    }

    public string GetMessage()
    {
        return message;
    }

    public void SetData(Data data)
    {
        this.data = data;

        UpdateImage(data);
        UpdateText(data);
    }

    public Data GetData()
    {
        return data;
    }

    public void UpdateImage(Data d)
    {
        if (rend)
        {
            tex.LoadImage(d.image);
        }
    } 

    public void UpdateText(Data d)
    {
        gestureString = d.gestureString;
        contourString = d.contourString;

        message = gestureString + contourString;
    }
    
}
