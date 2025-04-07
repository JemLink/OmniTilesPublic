using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;

// Needs to be attached to the upmost gameobject layer
public class CreateTileTexture : MonoBehaviour
{
    public Renderer rendToCopyFrom;
    public Texture text;
    public VideoPlayer videoPlayer;

    [Tooltip("This will be set by script and is just public for debugging purpose")]
    public TileShape tile;

    private void Awake()
    {
        tile = GetComponentInParent<TileShape>();
        if (!tile)
        {
            return;
        }

        videoPlayer = rendToCopyFrom.GetComponent<VideoPlayer>();
        if (videoPlayer)
        {
            VideoPlayer tileVideo = tile.gameObject.AddComponent<VideoPlayer>();
            tileVideo.clip = videoPlayer.clip;
            tileVideo.targetMaterialProperty = videoPlayer.targetMaterialProperty;
            tileVideo.Play();
        }
        else
        {
            text = rendToCopyFrom.material.GetTexture("_BaseMap");
            tile.GetComponent<Renderer>().material.color = rendToCopyFrom.material.color;
            tile.GetComponent<Renderer>().material.SetTexture("_BaseMap", text);
        }


        rendToCopyFrom.enabled = false;

    }
    
    
}
