using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class ShowPhoto : MonoBehaviour
{
    public Texture2D[] photos;

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    public void DisplayPhotos(List<TileShape> tiles)
    {
        int i = 0;
        foreach(TileShape tile in tiles)
        {
            //int i = tile.GetTextureID();
            //if(tile.prevID != tile.id)
            //{
                i++;
                tile.SetTextureID(i);
                tile.GetComponent<Renderer>().material.SetTexture("_BaseMap", photos[i % photos.Length]);
                tile.prevID = tile.id;
            //}
            
        }
    }
}
