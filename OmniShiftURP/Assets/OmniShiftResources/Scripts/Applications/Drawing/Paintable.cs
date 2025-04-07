using System.Collections;
using System.Collections.Generic;
using UnityEngine;

[RequireComponent(typeof(MeshRenderer), typeof(MeshCollider))]
public class Paintable : MonoBehaviour
{

    private Renderer rend;
    private MeshCollider col;
    private Texture2D tex;

    // Start is called before the first frame update
    void Awake()
    {
        col = GetComponent<MeshCollider>();
        if (col)
        {
            col.convex = false;
        }
       
        if (!rend)
        {
            rend = GetComponentInChildren<MeshRenderer>();
        }

        tex = rend.material.GetTexture("_BaseMap") as Texture2D;
        if (!tex)
        {
            float size = GetPixelSize(col);
            tex = new Texture2D((int)size, (int)size, TextureFormat.RGB24, mipChain: false);

            ColorTexture(tex, Color.black);
            rend.material.SetTexture("_BaseMap", tex);
        }
        else
        {
            if (!tex.isReadable)
            {
                tex = CreateReadableTexture(tex);
                float size = GetPixelSize(col);
                if (tex.width != (int)size)
                {
                    RescaleTexture(tex, (int)size, (int)size);
                }

                rend.material.SetTexture("_BaseMap", tex);
            }
            
        }
    }

    // Update is called once per frame
    void Update()
    {

    }

    public Texture2D InitBaseMap()
    {
        float size = GetPixelSize(col);
        tex = new Texture2D((int)size, (int)size, TextureFormat.RGB24, mipChain: false);

        ColorTexture(tex, Color.black);
        Debug.Log("Set tex to " + tex);
        rend.material.SetTexture("_BaseMap", tex);
        return tex;
    }

    public void SetTexture(Texture2D tex)
    {
        if (!rend)
        {
            rend = GetComponentInChildren<MeshRenderer>();
        }

        Texture2D baseTex = rend.material.GetTexture("_BaseMap") as Texture2D;
        if (baseTex && tex)
        {
            //Debug.Log("Set texture");
            rend.material.SetTexture("_BaseMap", tex);
            this.tex = tex;
        }
        else
        {
            Debug.Log("Something went wrong");
        }
        
    }

    private void ColorTexture(Texture2D tex, Color col)
    {
        if (!tex)
        {
            return;
        }

        var pixels = tex.GetPixels();

        for(int i = 0; i < pixels.Length; i++)
        {
            pixels[i] = col;
        }
        
        tex.SetPixels(pixels);
        tex.Apply();
    }


    private void RescaleTexture(Texture2D source, int width, int height)
    {
        var newPixels = new Color[width * height];
        for (int y = 0; y < height; y++)
        {
            for (int x = 0; x < width; x++)
            {
                float xFrac = ((float)x) / (width - 1);
                float yFrac = ((float)y) / (height - 1);
                newPixels[y * width + x] = source.GetPixelBilinear(xFrac, yFrac);
            }
        }

        source.Resize(width, height);
        source.SetPixels(newPixels);
        source.Apply();
    }


    private float GetPixelSize(MeshCollider col)
    {
        float diameter = col.bounds.extents.magnitude;
        Camera cam = GameObject.FindGameObjectWithTag("CapturingCamera").GetComponent<Camera>();
        float distance = Vector3.Distance(cam.transform.position, transform.position);
        float angularSize = (diameter / distance) * Mathf.Rad2Deg;

        float pixelSize = ((angularSize * Screen.height) / cam.fieldOfView);

        return pixelSize;
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

}
