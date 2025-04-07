using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// This class is just used to control if the tile already has an object with a behaviour
/// </summary>
public abstract class TileBehavior : MonoBehaviour
{
    public int ID;
    private void Start()
    {
        if (GetComponentInParent<TileShape>())
        {
            ID = GetComponentInParent<TileShape>().id;
        }
    }
}
