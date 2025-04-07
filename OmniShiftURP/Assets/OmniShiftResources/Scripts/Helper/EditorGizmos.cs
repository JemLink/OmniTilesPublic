using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EditorGizmos : MonoBehaviour
{
    public bool active;

    private void OnDrawGizmos()
    {
        if (active)
        {
            Gizmos.DrawWireMesh(gameObject.GetComponent<MeshFilter>().sharedMesh, transform.position, transform.rotation, transform.localScale);
            //Gizmos.DrawWireCube(transform.position, transform.lossyScale);
        }
        
    }

}
