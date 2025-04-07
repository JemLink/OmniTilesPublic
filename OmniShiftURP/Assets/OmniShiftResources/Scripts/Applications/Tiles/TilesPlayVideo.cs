using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;

public class TilesPlayVideo : MonoBehaviour
{
    [Tooltip("If set to true the audio sources will be played. Otherwise, the video sources will be played")]
    public bool playAudio;

    [Header("Audio Sources")]
    public AudioSource[] audios;

    [Header("Video Sources")]
    public VideoClip[] videos;
    

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {

    }

    public void PlayClip(List<TileShape> tiles)
    {
        if(tiles != null)
        {
            foreach(TileShape tile in tiles)
            {
                PlayClip(tile);
            }
        }
        
    }


    private void PlayClip(TileShape tile)
    {
        // change so it will not be destroyed
        tile.destroyWhenNotDetected = false;

        // check if tile is still detected or just hanging in scene
        // video/clip should play when tile is not detected
        if (tile.notDetected)
        {
            if (playAudio)
            {
                audios[tile.id % audios.Length].Play();
            }
            else
            {
                // need to add this to the tile before
                //Vector3 rot = Quaternion.ToEulerAngles(tile.transform.rotation);
                //rot = new Vector3(0, 0, rot.z);
                //tile.transform.rotation = Quaternion.Euler(rot);
                //tile.transform.rotation = Quaternion.Euler(Vector3.RotateTowards(transform.position, Camera.main.transform.position, 2, 2));
                VideoPlayer player = tile.GetComponent<VideoPlayer>();
                if (player)
                {
                    player.Play();
                }
                else
                {
                    player = tile.gameObject.AddComponent<VideoPlayer>();
                    player.isLooping = true;
                    player.targetMaterialProperty = "_BaseMap";
                    player.clip = videos[tile.id % videos.Length];
                    player.Play();
                }

            }
        }
        else
        {
            if (playAudio)
            {
                if (audios[tile.id % audios.Length].isPlaying)
                {
                    audios[tile.id % audios.Length].Pause();
                }

            }
            else
            {
                StartCoroutine(WaitForTileToBeTracked(tile));


            }
        }
    }

    IEnumerator WaitForTileToBeTracked(TileShape tile)
    {
        yield return new WaitForSecondsRealtime(0.5f);
        // need to add this to the tile before
        VideoPlayer player = tile.GetComponent<VideoPlayer>();
        if (player && player.isPlaying)
        {
            player.Pause();
        }
        else if (!player)
        {
            player = tile.gameObject.AddComponent<VideoPlayer>();
            player.isLooping = true;
            player.targetMaterialProperty = "_BaseMap";
            player.clip = videos[tile.id % videos.Length];
            player.Pause();
        }
    }
}
