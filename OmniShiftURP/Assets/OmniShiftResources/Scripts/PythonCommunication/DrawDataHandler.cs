using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DrawDataHandler : MonoBehaviour
{
    private DrawData data;
    public string message;
    public string centerMessage;

    public Vector3 center;
    public Brush brush;


    [Header("Debugging")]
    public bool brushAlwaysActive;


    [Header("Image handling")]
    private Texture2D tex;
    //public Renderer rend;

    
    [Header("Tiles Handling and Conversion to Unity space")]
    public Vector2 imageSize = new Vector2(800.0f, 800.0f);
    [Range(10f, 50.0f)]
    public float XYMovement = 30.0f;
    [Range(-6.0f, 6.0f)]
    public float xOffset = 0.0f;
    [Range(-6.0f, 6.0f)]
    public float yOffset = 0.0f;
    [Range(0.5f, 20.0f)]
    public float distanceScale = 15.0f;


    [Header("Test")]
    public GameObject testPositioning;


    // Start is called before the first frame update
    void Start()
    {
        //if (rend)
        //{
        //    tex = new Texture2D(800, 800, TextureFormat.RGB24, mipChain: false);
        //    rend.material.SetTexture("_BaseMap", tex);
        //    rend.material.color = Color.white;
        //}
    }

    

    public void SetMessage(string message)
    {
        this.message = message;
    }


    public string GetMessage()
    {
        return message;
    }


    public void SetData(DrawData d)
    {
        data = d;

        UpdateImage(data);
        UpdateText(data);
    }


    public DrawData GetData()
    {
        return data;
    }


    public void UpdateImage(DrawData d)
    {
        //if (rend)
        //{
        //    tex.LoadImage(d.image);
        //}
    }

    public void UpdateText(DrawData d)
    {
        centerMessage = d.centerMessage;

        message = centerMessage;

        //Debug.Log("Message " + message);

        HandleDrawing();
    }


    private void HandleDrawing()
    {
        if (!brushAlwaysActive)
        {
            if (!brush.active)
            {
                brush.SetActivationTo(true);
            }
            center = GetCenterFromMessage(centerMessage);
            Debug.DrawLine(center, Vector3.zero, Color.magenta);
            UpdateBrush(center);
        }
        else
        {
            brush.SetActivationTo(true);
        }
        
    }


    /// <summary>
    /// This message should have the form: cX,cY
    /// </summary>
    /// <param name="message"></param>
    /// <returns></returns>
    private Vector3 GetCenterFromMessage(string message)
    {
        if (message.Equals("NotDrawing"))
        {
            return new Vector3(-1, -1, -1);
        }
        else
        {
            string[] coords = message.Split(',');
            float x = float.Parse(coords[0]);
            float y = float.Parse(coords[1]);
            float z = -0.5f;

            return ConvertFromOpenCVToUnitySpace(new Vector3(x, y, z));
        }
        
    }


    private Vector3 ConvertFromOpenCVToUnitySpace(Vector3 openCVCoords)
    {
        //Debug.Log("open cv: " + openCVCoords);
        // map to range of 0 to 1
        float x = (openCVCoords.x / imageSize.x);
        float y = (openCVCoords.y / imageSize.y);

        // map of range from 0,1 to -1,1
        x = (x * 2.0f) - 1;
        y = (y * 2.0f) - 1;

        x *= XYMovement;
        y *= XYMovement;

        x += xOffset;
        y += yOffset;

        // z is in cm while Unity is in m
        // need to change it and adapt to camera pos
        float z = openCVCoords.z * 0.01f * distanceScale; // this is to change it to m

        return new Vector3(x, y, z);

    }


    private void UpdateBrush(Vector3 newPos)
    {
        if(newPos.Equals(new Vector3(-1, -1, -1)))
        {
            brush.SetActivationTo(false);
        }
        else
        {
            brush.transform.localPosition = newPos;
            brush.SetActivationTo(true);
        }
        
    }

    public void SetXOffset(float xOffset)
    {
        this.xOffset = xOffset;
    }

    public void SetYOffset(float yOffset)
    {
        this.yOffset = yOffset;
    }

    public void SetXYMovement(float XYMovement)
    {
        this.XYMovement = XYMovement;
    }
}
