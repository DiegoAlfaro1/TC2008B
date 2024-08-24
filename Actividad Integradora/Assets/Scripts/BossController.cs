using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;

public class BossController : MonoBehaviour
{

    public GameObject bulletSmall;
    public GameObject bulletMedium;
    public GameObject bulletBig;
    public Transform firePoint;
    public float fireRateCircle = 0.5f;
    public float fireRateBarrier = 0.5f;
    public float fireRateSpiral = 0.5f;

    public float velocidadRotacion = 30f;
    public float velocidadMovimiento = 1f;
    private float nextFire = 0.0f;
    private float modeTime = 10f;
    private float totalTime = 30f;
    private float mode = 1;

    void Update(){
        if(totalTime > 0){
            totalTime -= Time.deltaTime;

            modeTime -= Time.deltaTime;
            if(modeTime <= 0){
                mode = (mode % 3) + 1;
                modeTime = 10f;
            }

            switch(mode){
                case 1:
                    DisparosCirculares();
                    break;
                case 2:
                    DisparoBarrera();
                    break;
                case 3:
                    DisparosEspiral();
                    break;
            }
        }
    }

    void DisparosCirculares(){

        Vector3 targetPosition = new Vector3(0f, 6.5f, 0f);

        // Mover al boss hacia la posición objetivo de manera suave
        float step = velocidadMovimiento * Time.deltaTime;
        transform.position = Vector3.MoveTowards(transform.position, targetPosition, step);

        if (Time.time > nextFire){
            nextFire = Time.time + fireRateCircle;
            for (int i = 0; i < 8; i++){
                float angle = i * 45f + Time.time * velocidadRotacion;
                Vector3 dir = Quaternion.Euler(0, 0, angle) * Vector3.up;
                Instantiate(bulletSmall, firePoint.position, Quaternion.LookRotation(Vector3.forward, dir));
            }
        }
    }

    void DisparoBarrera(){
        if (Time.time > nextFire){
            nextFire = Time.time + fireRateBarrier;
            for (int i = -3; i <= 3; i++){
                Vector3 spawnPosition = new Vector3(firePoint.position.x + i * 1.5f, firePoint.position.y, firePoint.position.z);
                GameObject bullet = Instantiate(bulletMedium, spawnPosition, Quaternion.identity);
                
                // Rotar la bala para que apunte hacia abajo
                bullet.transform.rotation = Quaternion.Euler(0, 0, 180);
            }
        }

        float moveDirection = Mathf.Sin(Time.time * velocidadRotacion);
        transform.position = new Vector3(moveDirection * 5f, transform.position.y, transform.position.z);
    }

    void DisparosEspiral(){
        // Determinar la posición central de la pantalla
        Vector3 screenCenter = Camera.main.ScreenToWorldPoint(new Vector3(Screen.width / 2, Screen.height / 2, Camera.main.nearClipPlane));
        screenCenter.z = 0;

        // Mover al boss hacia el centro de manera suave
        float step = velocidadMovimiento * Time.deltaTime; // velocidadMovimiento es una nueva variable que defines
        transform.position = Vector3.MoveTowards(transform.position, screenCenter, step);

        if (Time.time > nextFire){
            nextFire = Time.time + fireRateSpiral;
            float angle = Time.time * velocidadRotacion * 2f;
            Vector3 dir = Quaternion.Euler(0, 0, angle) * Vector3.up;
            Instantiate(bulletBig, firePoint.position, Quaternion.LookRotation(Vector3.forward, dir));
        }
    }

}
