using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.Video;

// todo: change this into a list of tiles that is called at the end of the update function
/// <summary>
/// This class should get a list of the upodated tiles.
/// Every function using it should be able to handle things with just the list of tiles.
/// </summary>
/// 
//[System.Serializable]
//public class InteractableEvent : UnityEvent<TileShape> { }

[System.Serializable]
public class UpdateEvent : UnityEvent<List<TileShape>> { }

[System.Serializable]
public class ApplicationHandler : MonoBehaviour
{
    //public InteractableEvent onIDChange;
    public UpdateEvent onTilesUpdated;
    //public UpdateEvent onTilesConnected;
    public string photoPath;

    private Object[] textures;
    public TileShape testTile;

    [Header("All previously tracked Tiles")]
    Dictionary<int, TileShape> allTriangles = new Dictionary<int, TileShape>();
    Dictionary<int, TileShape> allSquares = new Dictionary<int, TileShape>();


    [Header("Test")]

    [Tooltip("If set to true the audio sources will be played. Otherwise, the video sources will be played")]
    public bool playAudio;

    [Header("Audio Sources")]
    public AudioSource[] audios;

    [Header("Video Sources")]
    public VideoClip[] videos;

    // Start is called before the first frame update
    void Start()
    {
        textures = Resources.LoadAll(photoPath, typeof(Texture2D));
    }

    // Update is called once per frame
    void Update()
    {
        
    }

    private void ChangePhoto(TileShape tile)
    {
        float xRot = tile.rotation.x;
        float yRot = tile.rotation.y;

        if (xRot > 180.0f)
        {
            xRot = 360.0f - xRot;
        }

        if (yRot > 180.0f)
        {
            yRot = 360.0f - yRot;
        }

        if (xRot > 40.0f || yRot > 40.0f)
        {
            int tileTexID = tile.GetTextureID();

            Texture2D tex = (Texture2D)textures[(tileTexID + 1) % textures.Length];
            tile.SetTextureID((tileTexID + 1) % textures.Length);

            Debug.Log("Tex should change");

            tile.gameObject.GetComponent<Renderer>().material.SetTexture("_BaseMap", tex);
        }
        

    }
    

    public void UpdateTexture(TileShape tile, int texID)
    {
        Texture2D tex = (Texture2D)textures[(texID + 1) % textures.Length];
        tile.SetTextureID((texID + 1) % textures.Length);

        Debug.Log("Tex should change");

        tile.gameObject.GetComponent<Renderer>().material.SetTexture("_BaseMap", tex);
    }
    


}
