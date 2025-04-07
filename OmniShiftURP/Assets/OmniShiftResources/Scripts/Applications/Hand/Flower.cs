using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Flower : MonoBehaviour
{
    public enum State { Blooming, Withering }
    public State state;
    
    public bool withered;
    public float directionOffset;

    public ParticleSystem flowerSystem;
    /// <summary>
    /// The force field should be turned off at the beginning
    /// </summary>
    public ParticleSystemForceField forceField;

    // Start is called before the first frame update
    void Start()
    {

    }

    // Update is called once per frame
    void Update()
    {
        if (!flowerSystem.IsAlive())
        {
            Destroy(this.gameObject);
        }

    }
    

    public void StartWithering(Vector3 windDirection)
    {
        flowerSystem.emissionRate = 0.0f;
        flowerSystem.loop = false;
        var externalForces = flowerSystem.externalForces;
        //externalForces.influenceMask = LayerMask.NameToLayer("Nothing");
        externalForces.influenceMask = 9;


        forceField.directionX = new ParticleSystem.MinMaxCurve(windDirection.x - directionOffset, windDirection.x + directionOffset);
        forceField.directionY = new ParticleSystem.MinMaxCurve(windDirection.x - directionOffset, windDirection.x + directionOffset);
        forceField.directionZ = new ParticleSystem.MinMaxCurve(windDirection.z - directionOffset, windDirection.z + directionOffset);

        StartCoroutine(Wither());
    }


    public void UpdatePosition(Transform trans)
    {
        gameObject.transform.position = trans.position;
    }

    IEnumerator Wither()
    {
        yield return new WaitForSeconds(0.5f);
        Destroy(forceField);
    }

}
