using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerAttackingBehaviour : GravityAffected
{
    [Header("Projectiles")]
    public GameObject projectilePrefab;
    public float zOffset;

    

    public void StartAttack()
    {
        GameObject tmp = Instantiate(projectilePrefab, transform.position + transform.forward * zOffset, transform.rotation);

        //tmp.GetComponent<GravityController>().gravityField = gravityField;
        //ProjectileBehaviour tmpProjectile = tmp.AddComponent<ProjectileBehaviour>();
        //tmp.GetComponent<ProjectileBehaviour>().gravityField = gravityField;
        tmp.GetComponent<ProjectileBehaviour>().StartShoot();
    }
    
}
