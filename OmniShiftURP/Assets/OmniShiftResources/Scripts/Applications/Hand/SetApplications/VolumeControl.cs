using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Video;


public class VolumeControl : WebbedHandApplications
{
    public AudioSource audioSource;
    public VideoPlayer videoPlayer;
    public enum ControlType { pause, lower, louder }

    public ControlType type;

    bool paused;

    // Start is called before the first frame update
    void Start()
    {
        audioSource.volume = 0.5f;
    }

    // Update is called once per frame
    void Update()
    {

    }


    public override void ExecuteApplication(Hand hand)
    {
        if (!active)
        {
            switch (type)
            {
                case ControlType.pause:
                    
                    if (paused)
                    {
                        paused = false;
                        PlaySources(true);
                    }
                    else
                    {
                        paused = true;
                        PlaySources(false);
                    }
                    
                    break;
                case ControlType.lower:

                    if (!paused)
                    {
                        Debug.Log("Lower");
                        ChangeVolumeOfSources(false);
                    }

                    break;
                case ControlType.louder:

                    if (!paused)
                    {
                        ChangeVolumeOfSources(true);
                    }

                    break;
                default:
                    Debug.LogError("Something went wrong in switch case statement");
                    break;
            }
        }


        active = true;
    }

    public override void StopApplication()
    {
        active = false;
    }


    private void ChangeVolumeOfSources(bool louder)
    {
        if (louder)
        {
            if (audioSource)
            {
                audioSource.volume = Mathf.Max(0.0f, (audioSource.volume + 0.1f));
            }

            if (videoPlayer)
            {
                videoPlayer.SetDirectAudioVolume(0, Mathf.Max(0.0f, (videoPlayer.GetDirectAudioVolume(0) + 0.1f)));
            }
        }
        else
        {
            if (audioSource)
            {
                audioSource.volume = Mathf.Max(0.0f, (audioSource.volume - 0.1f));
            }

            if (videoPlayer)
            {
                videoPlayer.SetDirectAudioVolume(0, Mathf.Max(0.0f, (videoPlayer.GetDirectAudioVolume(0) - 0.1f)));
            }
        }
    }

    private void PlaySources(bool play)
    {
        if (play)
        {
            if (audioSource)
            {
                audioSource.Play();
            }

            if (videoPlayer)
            {
                videoPlayer.Play();
            }
        }
        else
        {
            if (audioSource)
            {
                audioSource.Pause();
            }

            if (videoPlayer)
            {
                videoPlayer.Pause();
            }
        }
        
    }
}
