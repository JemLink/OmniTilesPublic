using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class TileParameters
{
    public int id;

    public Vector3 position;
    public Quaternion rotation;

    public TileParameters() { }

    public TileParameters(int id)
    {
        this.id = id;
    }

    public TileParameters(int id, Vector3 pos, Quaternion rot)
    {
        this.id = id;
        position = pos;
        rotation = rot;
    }


    public void UpdatePos(Vector3 pos)
    {
        position = pos;
    }

    public void UpdateRotation(Quaternion rot)
    {
        rotation = rot;
    }

    public void UpdateRotationAndPosition(Quaternion rot, Vector3 pos)
    {
        rotation = rot;
        position = pos;
    }
    
}