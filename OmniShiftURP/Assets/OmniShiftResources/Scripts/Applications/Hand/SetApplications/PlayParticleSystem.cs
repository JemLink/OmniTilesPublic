using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayParticleSystem : WebbedHandApplications
{
    public ParticleSystem particlesPrefab;
    private ParticleSystem particles;

    private void Start()
    {
        particles = Instantiate<ParticleSystem>(particlesPrefab, transform.position, Quaternion.identity, transform);
        particles.playOnAwake = false;
        particles.loop = false;
    }
    

    public override void ExecuteApplication(Hand hand)
    {
        active = true;
        StartPlayParticleSystem();
    }

    public override void StopApplication()
    {
        active = false;

        if (particles)
        {
            particles.Stop();
        }
    }

    private void StartPlayParticleSystem()
    {
        if (particles)
        {
            particles.Play();
        }
    }
    
}
