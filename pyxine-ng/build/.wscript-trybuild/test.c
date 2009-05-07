
#ifdef __cplusplus
extern "C" {
#endif
 void Py_Initialize(void);
 void Py_Finalize(void);
#ifdef __cplusplus
}
#endif
int main(int argc, char *argv[])
{
   argc++; /* avoid unused variable warning */
   argv++; /* avoid unused variable warning */
   Py_Initialize();
   Py_Finalize();
   return 0;
}
