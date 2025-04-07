using System.Collections;
using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// This class should handle and manage the different tiles that will be created. 
/// It should update lists of all the tiles and move them accordingly to their tracking.
/// </summary>
public class TilesHandler : MonoBehaviour
{
    [Header("Data")]
    private string triangleString;
    private string squareString;
    private string pentagonString;

    [Header("Materials")]
    public GameObject materialPrefab;
    //public GameObject trianglePrefab;
    //public GameObject squarePrefab;
    //public GameObject pentagonPrefab;

    [Header("Tiles Lists")]
    public List<Triangle> triangles;
    public List<Square> squares;
    public List<Pentagon> pentagons;

    [Header("Former Tiles ID and similarity List")]
    public Dictionary<int, int> allTriangles = new Dictionary<int, int>();
    public Dictionary<int, int> allSquares = new Dictionary<int, int>();
    public Dictionary<int, int> allPentagons = new Dictionary<int, int>();

    [Header("Tiles which will not be destroyed")]
    public List<Triangle> undestroyedTriangles;
    public List<Square> undestroyedSquares;
    public List<Pentagon> undestroyedPentagons;

    [Header("Parents")]
    public Transform triangleParent;
    public Transform squareParent;
    public Transform pentagonParent;

    [Header("Tile Values")]
    public Vector3 scale;

    [Header("Application Handling")]
    public ApplicationHandler tilesApplicationHandler;
    public float secondsTilDestroy;


    //[Header("Thresholds")]
    //[Tooltip("This is used to determine which tile is the closest one. " +
    //    "If a tile within this radius is detected, the tile will be updated")]
    //public float distanceThreshold;
    //[Tooltip("This is the threshold that needs to be overstepped for the position to be updated")]
    //public float positionThreshold;
    //[Tooltip("This is the threshold that needs to be overstepped for the rotation to be updated")]
    //public float rotationThreshold;





    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        
    }


    #region update tiles

    public void UpdateTriangles(List<Triangle> newTriangles)
    {
        UpdateListWOID<Triangle>(newTriangles, triangles, undestroyedTriangles, allTriangles, materialPrefab, triangleParent);
        if(triangles.Count > 0)
        {
            StartApplication<Triangle>(triangles);
        }

        if(undestroyedTriangles.Count > 0)
        {
            StartApplication<Triangle>(undestroyedTriangles);
        }
    }

    public void UpdateSquares(List<Square> newSquares)
    {
        UpdateListWOID<Square>(newSquares, squares, undestroyedSquares, allSquares, materialPrefab, squareParent);
        if(squares.Count > 0)
        {
            StartApplication<Square>(squares);
        }

        if (undestroyedSquares.Count > 0)
        {
            StartApplication<Square>(undestroyedSquares);
        }
    }

    public void UpdatePentagons(List<Pentagon> newPentagons)
    {
        UpdateListWOID<Pentagon>(newPentagons, pentagons, undestroyedPentagons, allPentagons, materialPrefab, pentagonParent);

        if(pentagons.Count > 0)
        {
            StartApplication<Pentagon>(pentagons);
        }

        if (undestroyedPentagons.Count > 0)
        {
            StartApplication<Pentagon>(undestroyedPentagons);
        }
    }

    protected void UpdateListWOID<T>(List<T> newList, List<T> oldList, List<T> notDestroyedList, Dictionary<int, int> allTiles, GameObject prefab, Transform parent) where T : TileShape, new()
    {
        // check if tiles is undestroyed list
        // if it is: add it to oldList
        UpdateNotDestroyedList(notDestroyedList, newList, oldList);

        // check if lists are same length

        // if new list is shorter
        if (newList.Count < oldList.Count)
        {
            // delete tiles that were not updated
            List<T> notUpdated = GetNotUpdatedTiles(newList, oldList);
            foreach(T t in notUpdated)
            {
                if (t.destroyWhenNotDetected)
                {
                    StartCoroutine(DestroyTileAfterSeeconds(t, secondsTilDestroy, oldList, notDestroyedList));
                    //oldList.Remove(t);
                    //Destroy(t.gameObject);
                }
                else
                {
                    // add it to list of undstroyed tiles
                    t.notDetected = true;
                    notDestroyedList.Add(t);
                    oldList.Remove(t);

                    // keep executing tiles application
                }
                
            }


        } 
        else if(newList.Count > oldList.Count)
        {
            // create new tiles and update old ones
            int diff = newList.Count - oldList.Count;
            for(int i = 0; i < diff; i++)
            {
                //GameObject tmpObj = Instantiate(prefab, Vector3.zero, Quaternion.identity, parent);
                GameObject tmpObj = TileGenerator.CreateTile(prefab, parent, Vector3.zero);
                T tmpTile = tmpObj.AddComponent<T>();
                tmpTile.UpdateTile(-1, Vector3.zero, Quaternion.identity);

                oldList.Add(tmpTile);
            }
            
        }
        

        // update tiles
        UpdateTiles(newList, oldList, allTiles);
    }



    private void UpdateNotDestroyedList<T>(List<T> notDestroyedList, List<T> newList, List<T> oldList) where T : TileShape, new()
    {
        foreach(T t in newList)
        {
            for(int i = 0; i < notDestroyedList.Count; i++)
            {
                if (t.id == notDestroyedList[i].id)
                {
                    notDestroyedList[i].notDetected = false;
                    oldList.Add(notDestroyedList[i]);
                    notDestroyedList.Remove(notDestroyedList[i]);
                    return;
                }
            }
        }
        
    }


    /// <summary>
    /// This will update the tiles and return the ones that were not updated in listToUpdate
    /// </summary>
    /// <typeparam name="T"></typeparam>
    /// <param name="newList"></param>
    /// <param name="oldList"></param>
    /// <returns></returns>
    private List<T> GetNotUpdatedTiles<T>(List<T> newList, List<T> listToUpdate) where T : TileShape, new()
    {
        List<T> notUpdated = new List<T>();

        if (newList.Count < listToUpdate.Count)
        {
            List<int> alreadyUpdatedIDs = new List<int>();
            for (int i = 0; i < newList.Count; i++)
            {
                int tmpTileID = -1;
                T tmpTile = GetNextTileExcept(newList[i], listToUpdate, alreadyUpdatedIDs, out tmpTileID);
                alreadyUpdatedIDs.Add(tmpTileID);
            }

            for(int i = 0; i < listToUpdate.Count; i++)
            {
                if (!alreadyUpdatedIDs.Contains(i))
                {
                    notUpdated.Add(listToUpdate[i]);
                }
            }

        }
        else
        {
            Debug.LogError("newList was longer than oldList. It needs to be shorter for the update");
        }

        return notUpdated;

    }


    /// <summary>
    /// This updates the tiles based on the next one found in distance. 
    /// It will also update the ids (so it does not take the id into account for finding the next tile)
    /// </summary>
    /// <typeparam name="T"></typeparam>
    /// <param name="newList"></param>
    /// <param name="oldList"></param>
    private void UpdateTiles<T>(List<T> newList, List<T> oldList, Dictionary<int, int> allTiles) where T : TileShape, new()
    {
        if(newList.Count != oldList.Count)
        {
            Debug.LogError("Could not update since lists are not same length");
        }
        else
        {
            List<int> alreadyUpdatedIDs = new List<int>();
            for(int i = 0; i < newList.Count; i++)
            {
                int tmpTileID = -1;
                T tmpTile = GetNextTileExcept<T>(oldList[i], newList, alreadyUpdatedIDs, out tmpTileID);
                //Debug.Log("ID tile " + tmpTile.id);

                // if the tile was newly created, the tile id will be -1
                if(oldList[i].id == -1)
                {
                    TileEntered(oldList[i], tmpTile, allTiles);
                }              

                oldList[i].UpdateTile(tmpTile.id, tmpTile.position, tmpTile.vertices);
                TileGenerator.UpdateTile(oldList[i].gameObject, oldList[i].vertices, scale);
                alreadyUpdatedIDs.Add(tmpTileID);
            }
        }
        
    }


    public void StartApplication<T>(List<T> tiles) where T : TileShape, new()
    {
        if (tiles.Count > 0)
        {
            //tilesApplicationHandler.onIDChange.Invoke(tiles[0]);

            List<TileShape> tilesList = new List<TileShape>();
            foreach (T t in tiles)
            {
                tilesList.Add((TileShape)t);
            }

            tilesApplicationHandler.onTilesUpdated.Invoke(tilesList);
        }

    }









    //protected void UpdateList<T>(List<T> newList, List<T> oldList, GameObject prefab, Transform parent) where T : TileShape, new()
    //{

    //    if (newList.Count > 0 || oldList.Count > 0)
    //    {
    //        if (newList.Count < oldList.Count)
    //        {
    //            // need to destroy tiles
    //            // update tiles that are still there
    //            List<T> notUpdated = new List<T>(oldList);
    //            for (int i = 0; i < newList.Count; i++)
    //            {
    //                T tmpTile = GetNextTileWithSameID<T>(newList[i], oldList);
    //                UpdateTile<T>(tmpTile, newList[i].position, newList[i].rotation);
    //                notUpdated.Remove(tmpTile);
    //            }

    //            foreach (T tile in notUpdated)
    //            {
    //                //Debug.Log("Remove tile " + tile.id);
    //                oldList.Remove(tile);
    //                Destroy(tile.gameObject);
    //            }


    //        }
    //        else if (newList.Count > oldList.Count)
    //        {
    //            // need to create new tiles

    //            // update oldList and take out tiles that have already been updated
    //            List<T> notUpdated = new List<T>();
    //            for (int i = 0; i < oldList.Count; i++)
    //            {
    //                T tmpTile = GetNextTileWithSameID<T>(oldList[i], newList);

    //                if(tmpTile.id != oldList[i].id)
    //                {
    //                    notUpdated.Add(oldList[i]);
    //                }
    //                else
    //                {
    //                    UpdateTile<T>(oldList[i], tmpTile.position, tmpTile.rotation);
    //                    newList.Remove(tmpTile);
    //                }

    //            }

    //            // add the other ones to oldList 
    //            CreateTiles<T>(newList, oldList, prefab, parent);
    //        }
    //        else
    //        {
    //            // both lists have same length

    //            // need to update positions
    //            List<T> notUpdated = new List<T>();
    //            for (int i = 0; i < oldList.Count; i++)
    //            {

    //                T tmpTile = GetNextTile<T>(oldList[i], newList);

    //                // if no tile with same id was found, -1 is returned
    //                //if (Vector3.Distance(tmpTile.position, oldList[i].position) > distanceThreshold)
    //                if(tmpTile.id == -1)
    //                {
    //                    // need to remove this tile and add new one
    //                    notUpdated.Add(oldList[i]);
    //                }
    //                else
    //                {
    //                    // check if id is wrong for last frame too or just an outlier
    //                    if(oldList[i].id != tmpTile.id)
    //                    {
    //                        if (oldList[i].prevID != tmpTile.id)
    //                        {
    //                            // need to remove this tile and add new one
    //                            notUpdated.Add(oldList[i]);
    //                        }
    //                    }
    //                    else
    //                    {
    //                        UpdateTile<T>(oldList[i], tmpTile.position, tmpTile.rotation);
    //                    }

    //                    oldList[i].prevID = tmpTile.id;

    //                }

    //                //T tmpTile = GetNextTileWithSameID<T>(oldList[i], newList);

    //                //// if no tile with same id was found, -1 is returned
    //                //if (tmpTile.id != oldList[i].id)
    //                //{
    //                //    // need to remove this tile and add new one
    //                //    notUpdated.Add(oldList[i]);
    //                //}
    //                //else
    //                //{
    //                //    UpdateTile<T>(oldList[i], tmpTile.position, tmpTile.rotation);
    //                //}


    //            }

    //            if (notUpdated.Count > 0)
    //            {
    //                foreach(T tile in notUpdated)
    //                {
    //                    if(tile && tile.gameObject)
    //                    {
    //                        oldList.Remove(tile);
    //                        Destroy(tile.gameObject);
    //                    }
    //                }
    //            }
    //        }
    //    }


    //}




    //protected T GetNextTileWithSameID<T>(T tile, List<T> tiles) where T : TileShape, new()
    //{
    //    float minDis = Mathf.Infinity;
    //    T closestTile = new T();
    //    closestTile.id = -1;
    //    foreach (T t in tiles)
    //    {
    //        float dist = Vector3.Distance(tile.position, t.position);
    //        if (t.id == tile.id && dist < minDis)
    //        {
    //            minDis = dist;
    //            closestTile = t;
    //        } 
    //    }
    //    return closestTile;
    //}

    protected T GetNextTile<T>(T tile, List<T> tiles) where T : TileShape, new()
    {
        float minDis = Mathf.Infinity;
        T closestTile = new T();
        closestTile.id = -1;
        foreach (T t in tiles)
        {
            float dist = Vector3.Distance(tile.position, t.position);
            if (dist < minDis)
            {
                minDis = dist;
                closestTile = t;
            }
        }
        return closestTile;
    }

    /// <summary>
    /// This will give the next tile (in distance) except for the ones specified in the except list.
    /// </summary>
    /// <typeparam name="T"></typeparam>
    /// <param name="tile"></param>
    /// <param name="tiles"></param>
    /// <returns></returns>
    protected T GetNextTileExcept<T>(T tile, List<T> tiles, List<int> excludedTilesIDs, out int closestTileID) where T : TileShape, new()
    {
        float minDis = Mathf.Infinity;
        T closestTile = new T();
        closestTile.id = -2;
        closestTileID = -1;
        T closestTileWithMatchingID = new T();
        closestTileWithMatchingID.id = -2;
        int closestTileIDWithMatchingID = -1;

        for (int i = 0; i < tiles.Count; i++)
        {
            if (excludedTilesIDs.Contains(i))
            {
                continue;
            }
            else
            {

                float dist = Vector3.Distance(tile.position, tiles[i].position);
                if (dist < minDis)
                {
                    minDis = dist;
                    closestTile = tiles[i];
                    closestTileID = i;

                    if(tile.id == tiles[i].id)
                    {
                        closestTileWithMatchingID = tiles[i];
                        closestTileIDWithMatchingID = i;
                    }
                }
            }
            
        }

        // This should work but I think the above is more elegant

        //foreach (T t in tiles)
        //{
        //    // the problem (I think) is that the tiles are not attached to anything, so the object is always null
        //    // therefore this contains might also return always null
        //    if (t.updated)
        //    {
        //        continue;
        //    }
        //    else
        //    {

        //        float dist = Vector3.Distance(tile.position, t.position);
        //        if (dist < minDis)
        //        {
        //            minDis = dist;
        //            closestTile = t;
        //        }
        //    }


        //}

        if (closestTileWithMatchingID.id != -2)
        {
            closestTile = closestTileWithMatchingID;
            closestTileID = closestTileIDWithMatchingID;
        }

        closestTile.updated = true;
        return closestTile;
    }


    private void UpdateTile<T>(T tile, Vector3 position, Vector3[] vertices) where T : TileShape, new()
    {
        if (tile)
        {
            //tile.SetPosition(position);
            //tile.UpdateRotation(rotation);
            tile.UpdateVertices(vertices);
            tile.UpdatePosition();
        }
        
    }


    public void TileEntered(TileShape oldTile, TileShape tmpTile, Dictionary<int, int> allTiles)
    {
        if (!allTiles.ContainsKey(oldTile.id))
        {
            Debug.Log("Tile found");
        }
        //int textureID = GetTextureIDIfTracked(tmpTile, allTiles);
        //Debug.Log("Text id " + textureID);
        //if (textureID != -1)
        //{
        //    Debug.Log("Seen tile");
        //    oldTile.SetTextureID(textureID);
        //    tilesApplicationHandler.UpdateTexture(oldTile, textureID);
        //}
        //else
        //{
        //    // add this tile since it has not been tracked before
        //    allTiles.Add(tmpTile.id, 0);
        //}
    }


    /// <summary>
    /// This returns the texture id of the tile if it has been tracked before and -1 otherwise
    /// </summary>
    /// <typeparam name="T"></typeparam>
    /// <param name="tile"></param>
    /// <param name="allTiles"></param>
    /// <returns></returns>
    private int GetTextureIDIfTracked<T>(T tile, Dictionary<int, int> allTiles) where T : TileShape, new()
    {
        //if(allTiles != null)
        //{
        //    foreach (KeyValuePair<int, int> keyValue in allTiles)
        //    {
        //        if (keyValue.Key == tile.id)
        //        {
        //            Debug.Log("Found tile: " + keyValue.Key);
        //            Debug.Log("Found tile texture: " + keyValue.Value);
        //            return keyValue.Value;
        //        }
        //    }
        //}

        if (allTiles.ContainsKey(tile.id))
        {
            return allTiles[tile.id];
        }
        
        
        return -1;
    }


    #endregion


    #region tile creation

    //private void CreateTiles<T>(List<T> tilesToCreate, List<T> listToAdd, GameObject prefab, Transform parent) where T : TileShape, new()
    //{
    //    foreach(T tile in tilesToCreate)
    //    {
    //        GameObject tmpObj = Instantiate(prefab, tile.position, tile.rotation, parent);
    //        T tmpTile = tmpObj.AddComponent<T>();

    //        tmpTile.id = tile.id;
    //        tmpTile.UpdatePosition(tile.position);
    //        //tmpTile.UpdateRotation(tile.rotation);
    //        tmpTile.UpdateVertices(tile.vertices);
            
    //        listToAdd.Add(tmpTile);
    //    }
        
    //}


    // these should later check if the shape already exist


    public void CreateTriangle(float area, Vector3 center, Vector3[] vertices)
    {
        GameObject tmpObj = Instantiate(materialPrefab, center, Quaternion.identity, triangleParent);
        Triangle tmpTri = tmpObj.AddComponent<Triangle>();

        tmpTri.SetPosition(center);
        //tmpTri.UpdateRotation();

        triangles.Add(tmpTri);

    }

    public void CreateSquare(float area, Vector3 center, Vector3[] vertices)
    {
        GameObject tmpObj = Instantiate(materialPrefab, center, Quaternion.identity, squareParent);
        Square tmpSqu = tmpObj.AddComponent<Square>();

        tmpSqu.SetPosition(center);
        //tmpSqu.UpdateRotation();

        squares.Add(tmpSqu);
    }

    public void CreatePentagon(float area, Vector3 center, Vector3[] vertices)
    {
        GameObject tmpObj = Instantiate(materialPrefab, center, Quaternion.identity, pentagonParent);
        Pentagon tmpPen = tmpObj.AddComponent<Pentagon>();

        tmpPen.SetPosition(center);
        //tmpPen.UpdateRotation();

        pentagons.Add(tmpPen);
    }


    #endregion


    IEnumerator DestroyTileAfterSeeconds<T>(T tile, float seconds, List<T> oldList, List<T> notDestroyedList) where T : TileShape, new()
    {
        tile.notDetected = true;
        notDestroyedList.Add(tile);
        oldList.Remove(tile);

        yield return new WaitForSecondsRealtime(seconds);

        if (tile && tile.notDetected)
        {
            notDestroyedList.Remove(tile);
            Destroy(tile.gameObject);
        }
        
    }
}
