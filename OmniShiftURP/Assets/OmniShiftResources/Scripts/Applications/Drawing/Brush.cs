using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

[System.Serializable]
public class DrawingEvent : UnityEvent<RaycastHit> { }
[System.Serializable]
public class RaycastHitvent : UnityEvent<RaycastHit> { }


public class Brush : MonoBehaviour
{
    public bool active;

    [Header("Other Hitting behaviours")]
    public RaycastHitvent OnRaycastHit;
    public DrawingEvent OnDraw;

    [Header("Brush Paramter")]
    Camera capturingCam;
    Texture2D brushTex;
    public Vector2 brushSize;


    // Start is called before the first frame update
    void Start()
    {
        capturingCam = GameObject.FindGameObjectWithTag("CapturingCamera").GetComponent<Camera>();
        brushTex = CreateReadableTexture(GetComponent<Renderer>().material.mainTexture as Texture2D);
        RescaleTexture(brushTex, (int)brushSize.x, (int)brushSize.y);
    }

    private void OnValidate()
    {
        if (brushTex)
        {
            RescaleTexture(brushTex, (int)brushSize.x, (int)brushSize.y);
        }
        
    }

    // Update is called once per frame
    void Update()
    {
        Shader.SetGlobalVector("BrushPos", transform.position);

        if (active)
        {
            var Ray = new Ray(transform.position, Vector3.forward); // capturingCam.ScreenPointToRay(brush.transform.position);

            Debug.DrawRay(transform.position - Vector3.forward, Vector3.forward);
            RaycastHit hit;
            if (Physics.Raycast(Ray, out hit))
            {
                OnRaycastHit.Invoke(hit);

            }
        }

    }


    public void SetActivationTo(bool active)
    {
        this.active = active;
        GetComponent<Renderer>().enabled = active;
    }


    public void RescaleBrush(Vector2 newScale)
    {
        brushSize = newScale;
        brushTex = CreateReadableTexture(GetComponent<Renderer>().material.mainTexture as Texture2D);
        RescaleTexture(brushTex, (int)brushSize.x, (int)brushSize.y);
    }
    

    public void Draw(RaycastHit hit)
    {
        if (hit.transform.GetComponentInChildren<Paintable>())
        {
            Renderer rend = hit.transform.GetComponentInChildren<Renderer>();
            MeshCollider col = hit.collider as MeshCollider;


            if (rend && rend.material != null && rend.material.GetTexture("_BaseMap") != null && col)
            {
                //Debug.Log("Hit texture");
                Texture2D tex = rend.material.GetTexture("_BaseMap") as Texture2D;
                if (!tex.isReadable)
                {
                    Debug.Log("Convert texture to readbale: " + tex.isReadable);
                    tex = CreateReadableTexture(tex);
                    RescaleTexture(tex, 800, 800);
                    rend.material.SetTexture("_BaseMap", tex as Texture2D);
                }
                Vector2 pixelUV = hit.textureCoord;
                pixelUV.x *= tex.width;
                pixelUV.y *= tex.height;

                DrawTexture(pixelUV, tex);
                OnDraw.Invoke(hit);
            }
        }
        
    }


    private void DrawTexture(Vector2 uvs, Texture2D originalTex)
    {
        uvs -= Vector2.one * brushTex.width * 0.5f;

        for (int i = 0; i < brushTex.width; i++)
        {
            for (int j = 0; j < brushTex.height; j++)
            {
                int xPos = Mathf.Clamp((int)(uvs.x + i), 0, originalTex.width);
                int yPos = Mathf.Clamp((int)(uvs.y + j), 0, originalTex.height);
                Color texCol = originalTex.GetPixel(xPos, yPos);
                Color brushCol = GetComponent<Renderer>().material.color;
                Color col = Color.Lerp(texCol, brushCol, brushTex.GetPixel(i, j).a);
                originalTex.SetPixel(xPos, yPos, col);

            }
        }

        originalTex.Apply();
    }

    private Texture2D CreateReadableTexture(Texture2D origin)
    {
        RenderTexture renderTex = RenderTexture.GetTemporary(
            (int)origin.width,
            (int)origin.height,
            0,
            RenderTextureFormat.Default,
            RenderTextureReadWrite.Linear);

        Graphics.Blit(origin, renderTex);
        RenderTexture previous = RenderTexture.active;
        RenderTexture.active = renderTex;
        Texture2D readableText = new Texture2D((int)origin.width, (int)origin.height);
        readableText.ReadPixels(new Rect(0, 0, renderTex.width, renderTex.height), 0, 0);
        readableText.Apply();
        RenderTexture.active = previous;
        RenderTexture.ReleaseTemporary(renderTex);
        return readableText;
    }

    private void RescaleTexture(Texture2D source, int width, int height)
    {
        var newPixels = new Color[width * height];
        for(int y = 0; y < height; y++)
        {
            for(int x = 0; x < width; x++)
            {
                newPixels[y * width + x] = source.GetPixelBilinear(((float)x) / width, ((float)y) / height);
            }
        }

        source.Resize(width, height);
        source.SetPixels(newPixels);
        source.Apply();
    }


    public void ChangeTextureTo(Texture2D newTex)
    {
        brushTex = CreateReadableTexture(newTex);
        RescaleTexture(brushTex, (int)brushSize.x, (int)brushSize.y);
        GetComponent<Renderer>().material.SetTexture("_BaseMap", brushTex);
    }


    public void ChangeColor(float value, Vector3 affectedValue)
    {
        Vector3 changedColors = Vector3.one - affectedValue;
        Color brushCol = this.GetComponent<Renderer>().material.color;
        Color newCol = new Color(brushCol.r * changedColors.x, brushCol.g * changedColors.y, brushCol.b * changedColors.z);

        GetComponent<Renderer>().material.color = new Color(newCol.r + affectedValue.x * value, newCol.g + affectedValue.y * value, newCol.b + affectedValue.z * value);
    }
}
