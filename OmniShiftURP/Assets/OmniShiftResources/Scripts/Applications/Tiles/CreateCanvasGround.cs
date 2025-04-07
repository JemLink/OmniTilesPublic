using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class CreateCanvasGround : MonoBehaviour
{
    [Header("Image handling")]
    private Texture2D tex;
    public Renderer bg;
    //public Material canvasMat;

    [Header("Brush Handling")]
    public Brush brush;
    public Toggle drawToggle;
    public Button DrawButton;
    public Button[] patternButtons;
    public Slider brushSize;
    public Slider redSlider;
    public Slider greenSlider;
    public Slider blueSlider;

    [Header("In Scene UI")]
    public InSceneSlider redInSceneSlider;
    public InSceneSlider greenInSceneSlider;
    public InSceneSlider blueInSceneSlider;

    Dictionary<int, Texture2D> formerTextures;
    [Serializable]
    public struct FormerTexts { public int id; public Texture2D tex; }
    public List<FormerTexts> texts;

    // Start is called before the first frame update
    void Start()
    {
        formerTextures = new Dictionary<int, Texture2D>();

        if (bg)
        {
            tex = new Texture2D(800, 800, TextureFormat.RGB24, mipChain: false);
            bg.material.SetTexture("_BaseMap", tex);
            bg.material.color = Color.white;
        }

        if (DrawButton)
        {
            DrawButton.onClick.AddListener(() => PythonCommunicationHandler.Instance.ChangeActiveClient());
        }
        

        if (redSlider)
        {
            Color col = brush.GetComponent<Renderer>().material.color;
            redSlider.onValueChanged.AddListener(delegate { ChangeBrushColorFromUISlider(redSlider.value); });
        }

        if (blueSlider)
        {
            Color col = brush.GetComponent<Renderer>().material.color;
            blueSlider.onValueChanged.AddListener(delegate { ChangeBrushColorFromUISlider(blueSlider.value); });
        }

        if (greenSlider)
        {
            Color col = brush.GetComponent<Renderer>().material.color;
            greenSlider.onValueChanged.AddListener(delegate { ChangeBrushColorFromUISlider(greenSlider.value); });
        }


        if (redInSceneSlider)
        {
            Color col = brush.GetComponent<Renderer>().material.color;
            redInSceneSlider.OnSliderMove.AddListener(delegate { ChangeBrushColorFormInSceneUI(redInSceneSlider.value); });
        }

        if (greenInSceneSlider)
        {
            Color col = brush.GetComponent<Renderer>().material.color;
            greenInSceneSlider.OnSliderMove.AddListener(delegate { ChangeBrushColorFormInSceneUI(greenInSceneSlider.value); });
        }

        if (blueInSceneSlider)
        {
            Color col = brush.GetComponent<Renderer>().material.color;
            blueInSceneSlider.OnSliderMove.AddListener(delegate { ChangeBrushColorFormInSceneUI(blueInSceneSlider.value); });
        }

        brushSize.onValueChanged.AddListener(delegate { ChangeBrushSize(brushSize.value); });
    }

    // Update is called once per frame
    void Update()
    {

    }


    public void CreateCanvasTile(List<TileShape> tiles)
    {
        foreach (TileShape tile in tiles)
        {
            // add stuff needed for painting
            AddPaintable(tile);
        }
    }


    private void AddPaintable(TileShape tile)
    {
        MeshGenerator meshGen = tile.GetComponentInChildren<MeshGenerator>();
        Mesh mesh = meshGen.GetMesh();
        MeshRenderer rend = meshGen.GetComponent<MeshRenderer>();
        MeshCollider col = meshGen.GetComponent<MeshCollider>();


        Paintable canvas = meshGen.GetComponent<Paintable>();
        if (!canvas)
        {
            //Debug.Log("Was not paintable");
            Paintable paint = meshGen.gameObject.AddComponent<Paintable>();
            if (formerTextures.ContainsKey(tile.id))
            {
                //Debug.Log("Should set old texture: " + tile.id);
                paint.SetTexture(formerTextures[tile.id]);
            }
            else
            {
                Texture2D tex = paint.GetComponentInChildren<MeshRenderer>().material.GetTexture("_BaseMap") as Texture2D;
                if (tex != null)
                {
                    formerTextures.Add(tile.id, tex);
                    FormerTexts tmp = new FormerTexts();
                    tmp.id = tile.id;
                    tmp.tex = tex;
                    texts.Add(tmp);
                    paint.SetTexture(tex);
                }

            }
        }
        else
        {
            col.sharedMesh = mesh;
        }

    }


    private void ChangeBrushColorFormInSceneUI(float sliderValue)
    {
        Color col = new Color(redInSceneSlider.value, greenInSceneSlider.value, blueInSceneSlider.value);
        //Debug.Log("Set color to " + col);
        brush.GetComponent<Renderer>().material.color = col;
    }

    private void ChangeBrushColorFromUISlider(float sliderValue)
    {
        Color col = new Color(redSlider.value, greenSlider.value, blueSlider.value);
        //Debug.Log("Set color to " + col);
        brush.GetComponent<Renderer>().material.color = col;
    }


    public void ChangeBrushPattern(Texture2D newText)
    {
        brush.ChangeTextureTo(newText);
    }


    private void ChangeBrushColor(Color col)
    {
        //Debug.Log("Set color to " + col);
        brush.GetComponent<Renderer>().material.color = col;
    }


    private void ChangeBrushSize(float size)
    {
        brush.RescaleBrush(new Vector2(size, size));
    }


}
