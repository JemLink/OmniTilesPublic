using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DeathZone : MonoBehaviour
{

    private void OnTriggerEnter(Collider other)
    {
        Debug.Log("Detected something");
        if (other.gameObject.CompareTag("Player"))
        {
            Debug.Log("Destroy player");
            Destroy(other.gameObject);
        }
    }

    private void OnCollisionEnter(Collision collision)
    {
        Debug.Log("Detected something");
        if (collision.gameObject.CompareTag("Player"))
        {
            Debug.Log("Destroy player");
            Destroy(collision.gameObject);
        }
    }
    

    private void OnDrawGizmos()
    {
        Gizmos.DrawWireCube(transform.position, Vector3.Scale(transform.localScale, new Vector3(10.0f, 10.0f, 0.1f)));
        
    }
}
