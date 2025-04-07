using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class Hourglass : TileBehavior
{
    public float startTime;
    public float timer;
    public float timeToFall;
    public ParticleSystem sandUp;
    public ParticleSystem sandDown;
    public Transform up;

    public GameObject sandTop;
    public GameObject sandBottom;

    private Vector3 currentUp;

    // Start is called before the first frame update
    void Start()
    {
        currentUp = sandTop.transform.position - sandBottom.transform.position;
        StartCoroutine(Timer());
        sandBottom.transform.localScale = Vector3.zero;

        if (GetComponentInParent<TileShape>())
        {
            ID = GetComponentInParent<TileShape>().id;
        }
    }

    // Update is called once per frame
    void Update()
    {
        SandRun();
    }

    private void SandRun()
    {
        Vector3 direction = sandTop.transform.position - sandBottom.transform.position;

        if (Vector3.Dot(currentUp, direction) < 0)
        {
            // hourglass was flipped
            FlipHourglass();
        }

        StartCoroutine(ResizeToTimer(sandTop, false));
        StartCoroutine(ResizeToTimer(sandBottom, true));

    }

    private void FlipHourglass()
    {
        GameObject tmpObject = sandTop;
        sandTop = sandBottom;
        sandBottom = tmpObject;

        ParticleSystem tmpPart = sandUp;
        sandUp = sandDown;
        sandDown = tmpPart;

        sandDown.Stop();
        sandUp.Play();

        StopAllCoroutines();

        if(timer <= 0)
        {
            timer = startTime;
        }
        else
        {
            timer = startTime - timer;
        }
        
        StartCoroutine(Timer());


    }

    IEnumerator ResizeToTimer(GameObject obj, bool bigger)
    {
        float ratio = timer / startTime;
        float scale = 1.0f;


        if (bigger)
        {
            yield return new WaitForSecondsRealtime(timeToFall);
            scale = (1.0f - ratio);
        }
        else
        {
            scale = ratio;
        }

        obj.transform.localScale = new Vector3(scale, scale, scale);
    }


    IEnumerator Timer()
    {
        while (timer > 0)
        {
            yield return new WaitForSeconds(0.1f);
            timer -= 0.1f;
        }


        sandUp.Stop();
    }
}
